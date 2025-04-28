import os
import sys
import types
import base64
import getpass
import requests
import importlib
from request import Request

from dotenv import load_dotenv
from .Instance import Instance

load_dotenv()


class Dropped:
    """A class to handle dropping items from a user's inventory.

    This class processes item drops by removing them from the inventory system
    and creating local files from the item data.

    :ivar item_names: List of items to be dropped from inventory
    :type item_names: list
    """

    def __init__(self, item_names: list = []):
        """Initialize the drop process for multiple items.

        :param item_names: List of item names to drop
        :type item_names: list, optional
        :return: None
        :rtype: None
        """
        for item in item_names:
            self.__drop_item(item)

    def __drop_item(self, item_name: str = "") -> None:
        """Drop a single item from inventory and create a local file.

        :param item_name: Name of item to drop
        :type item_name: str, optional
        :return: None
        :rtype: None
        :raises requests.exceptions.RequestException: If the API request fails
        :raises IOError: If there are issues writing the file
        """
        item_record = self.__search_inventory(item_name)
        item_binary = self.__convert_to_py_file(item_record["item_bytestring"])
        with open(f"{item_name}.py", "w") as fh:
            fh.write(item_binary)
        status = Request(
            method="PATCH",
            url=f"{os.getenv('API_URL')}:{os.getenv('API_PORT')}/v1/inventory/reduce/",
            data={
                "item_name": item_name,
                "item_owner": os.getenv("INPACK")
                if os.getenv("INPACK")
                else os.getenv("GITHUB_USER") or getpass.getuser(),
                "item_drop": True,
            },
        )()

    def __search_inventory(self, item_name: str = "") -> dict:
        """Search for an item in the user's inventory.

        :param item_name: Name of item to search for
        :type item_name: str, optional
        :return: Item record if found
        :rtype: dict
        :raises requests.exceptions.RequestException: If the API request fails
        """
        item = Request(
            method="POST",
            url=f"{os.getenv('API_URL')}:{os.getenv('API_PORT')}/v1/inventory/search/",
            data={
                "charname": os.getenv("INPACK")
                if os.getenv("INPACK")
                else os.getenv("GITHUB_USER") or getpass.getuser(),
                "item_name": item_name,
            },
        )()
        return item.json()

    def __convert_to_py_file(self, item_binary) -> str:
        """Convert binary item data to Python source code.

        :param item_binary: Hex-encoded binary data of Python file
        :type item_binary: str
        :return: Decoded Python source code
        :rtype: str
        :raises ValueError: If binary data cannot be decoded
        """
        source = bytes.fromhex(item_binary).decode("utf-8")
        return source


def cmd():
    """Command entry point for dropping items.

    Processes command line arguments and initializes item dropping.

    :raises SystemExit: If no items are specified to drop
    :return: None
    :rtype: None
    """
    Dropped(sys.argv[1:])
