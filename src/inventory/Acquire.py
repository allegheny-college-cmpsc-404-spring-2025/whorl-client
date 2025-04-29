import io
import os
import sys
import base64
import pathlib
import pennant
import requests
import zipfile
import getpass
import importlib
import tempfile
import shutil
from request import Request

from .Instance import Instance
from .specs import ItemSpec
from .Exceptions import InvalidCommandException, InvalidArgumentsException

from dotenv import load_dotenv

load_dotenv()

class Acquisition:
    """A class to handle acquiring and transmitting new items to the inventory system.

    This class processes item acquisitions by validating files and transmitting them
    to the inventory API endpoint.

    :ivar sys.argv: Command line arguments containing files to process
    :type sys.argv: list
    """

    def __init__(self):
        """Initialize the acquisition process for multiple files.

        Processes all files provided as command line arguments, creating
        Instance objects and transmitting them to the API.

        :return: None
        :rtype: None
        :raises FileNotFoundError: If specified files don't exist
        :raises requests.exceptions.RequestException: If API transmission fails
        """
        # Accommodate multiple files; acquire each serially
        for file in sys.argv[1:]:
            # this is the handling for .pyz files
            if file.endswith('.pyz'):
                if self.__validate_pyz_file(file):
                    self.__handle_pyz_file(file)
                else:
                    # validation failed message already printed
                    pass
            else:
                instance = Instance(file)
                if instance.valid:
                    self.__transmit_to_api(instance)

    def __validate_pyz_file(self, pyz_file):
        """Handle a .pyz file by sending it directly to the API.

        :param pyz_file: Path to the .pyz file
        :type pyz_file: str
        :return: bool
        """
        if not os.path.exists(pyz_file):
            print(f"Error: {pyz_file} not found!")
            return False

        # get expected item name from filename (without .pyz extension)
        item_name = os.path.basename(pyz_file).split('.')[0]

        # create a temporary directory to extract the .pyz contents
        temp_dir = tempfile.mkdtemp()
        try:
            # extract contents
            with zipfile.ZipFile(pyz_file, 'r') as zipf:
                zipf.extractall(temp_dir)

            # add the temp directory to path so we can import
            sys.path.insert(0, temp_dir)

            # check if main module file exists
            module_path = os.path.join(temp_dir, f"{item_name}.py")
            if not os.path.exists(module_path):
                print(f"Error: {item_name}.py not found in {pyz_file}")
                return False

            # try direct module validation first - this often works better for .pyz files
            try:
                # import the module directly
                module = importlib.import_module(item_name)

                # check if the module has a class with the same name
                if not hasattr(module, item_name):
                    print(f"Error: {item_name} module does not contain {item_name} class")
                    return False
                # get the class from the module
                item_class = getattr(module, item_name)

                # Check if the class inherits from ItemSpec
                if not issubclass(item_class, ItemSpec):
                    print(f"Error: {item_name} class does not inherit from ItemSpec")
                    return False
                # check if the class has a use method
                if not hasattr(item_class, 'use'):
                    print(f"Error: {item_name} class does not have a use method")
                    return False
                return True
            except ImportError as e:
                # fall back to Instance validation if direct validation fails
                print(f"Direct validation failed, trying Instance validation: {e}")

            # Use the Instance class for validation
            instance = Instance(module_path)
            return instance.valid
        except Exception as e:
            print(f"Error validating {pyz_file}: {e}")
            return False
        finally:
            # clean up
            if temp_dir in sys.path:
                sys.path.remove(temp_dir)
            shutil.rmtree(temp_dir)

    def __handle_pyz_file(self, pyz_file):
        """Handle a .pyz file by sending it directly to the API."""

        try:
            # get the item name from the filename
            item_name = os.path.basename(pyz_file).split('.')[0]

            # create basic item properties
            data = {
                "item_name": item_name,
                "item_owner": os.getenv("GITHUB_USER") or getpass.getuser(),
                "item_weight": 1,
                "item_qty": 1,
                "item_consumable": True,
                "item_version": "1.0.0",
                "item_type": "pyz"
            }

            # read the file as binary
            with open(pyz_file, 'rb') as f:
                buffer = io.BytesIO(f.read())

            # send it to the API
            response = Request(
                method="POST",
                url=f"{os.getenv('API_URL')}:{os.getenv('API_PORT')}/v1/inventory/add/",
                data=data,
                files={"item_binary": buffer},
            )()

            # this is my debuggin code, remove later
            if response.status_code == 200:
                print(f"Successfully added {item_name} to inventory!")
            elif response.status_code == 409:
                context = response.json()
                print(context["error"])
            else:
                print(f"Failed to add {item_name} to inventory! Status code: {response.status_code}")
                
        except Exception as e:
            print(f"Error processing {pyz_file}: {str(e)}")

    def __compress_file(self, instance: dict = {}) -> str:
        """Compress file into an actual zip archive, rather than just a single
        item or folder

        :param instance: Instance object containing item data and binary content
        """
        buffer = io.BytesIO()
        binary = instance.binary.read()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED, False) as fh:
            fh.writestr(instance.name, binary)
        return buffer.getvalue().hex()


    def __transmit_to_api(self, instance: dict = {}) -> None:
        """Transmit an item instance to the inventory API.

        :param instance: Instance object containing item data and binary content
        :type instance: Instance
        :return: None
        :rtype: None
        :raises requests.exceptions.RequestException: If the API request fails
        """
        response = Request(
            method="POST",
            url=f"{os.getenv('API_URL')}:{os.getenv('API_PORT')}/v1/inventory/add/",
            data=instance.transmit,
            files={"item_binary": self.__compress_file(instance)},
        )()
        if response.status_code == 409:
            context = response.json()
            print(context["error"])


def cmd():
    """Command entry point for the get command.

    Validates command usage and initializes item acquisition.

    :raises InvalidCommandException: If not called via the 'get' command
    :raises InvalidArgumentsException: If no item names are provided
    :return: None
    :rtype: None
    """
    # Validate correct use of function
    try:
        if sys.argv[0].split("/")[-1] != "get":
            raise InvalidCommandException("Cannot call Acqusition directly!")
    except InvalidCommandException as e:
        print(e)
        sys.exit(1)
    try:
        if len(sys.argv) < 2:
            raise InvalidArgumentsException("At least one item name required!")
    except InvalidArgumentsException as e:
        print(e)
        sys.exit(1)
    # Failing any issues, add CWD to the path and
    # start Acquisition
    sys.path.append(os.path.expanduser(os.getcwd()))
    Acquisition()
