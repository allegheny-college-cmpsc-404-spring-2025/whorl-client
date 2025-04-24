import io
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


class Usage:
    """A class to handle using and inspecting items from inventory.

    This class processes item usage by retrieving items from inventory,
    decoding their contents, and executing their use functionality.

    :ivar item_name: Name of the item to use or inspect
    :type item_name: str
    :ivar source: Decoded source code of the item
    :type source: str
    """

    def __init__(self, item_name: str = "", to_use: bool = True):
        """Initialize item usage process.

        :param item_name: Name of item to use
        :type item_name: str, optional
        :param to_use: Whether to use or just inspect the item
        :type to_use: bool, optional
        :return: None
        :rtype: None
        :raises SystemExit: If item is not found in inventory
        """
        self.item_name = item_name
        item_record = self.__search_inventory()
        if not item_record:
            print(f"ERROR: You don't seem to have any {item_name}!")
            sys.exit(1)
        self.__decode_item_file(item_record)
        if to_use:
            self.__use_item()
        else:
            self.__get_info()

    def __search_inventory(self, item_name: str = "") -> dict:
        """Search for an item in the user's inventory.

        :param item_name: Name of item to search for
        :type item_name: str, optional
        :return: Item record if found, empty dict if not found
        :rtype: dict
        :raises requests.exceptions.RequestException: If the API request fails
        """
        item = Request(
            "POST",
            url=f"{os.getenv('API_URL')}:{os.getenv('API_PORT')}/v1/inventory/search/",
            data={
                "charname": os.getenv("GITHUB_USER") or getpass.getuser(),
                "item_name": self.item_name,
            },
        )()
        if item.status_code == 200:
            return item.json()
        return {}

    def __decode_item_file(self, item_record: dict = {}) -> None:
        """Decode hex-encoded item binary data into source code.

        :param item_record: Dictionary containing item data including binary content
        :type item_record: dict
        :return: None
        :rtype: None
        :raises ValueError: If binary data cannot be decoded
        """
        self.source = bytes.fromhex(item_record["item_bytestring"]).decode("utf-8")

    def __use_item(self):
        """Execute an item's use functionality and update inventory.

        :return: None
        :rtype: None
        :raises AttributeError: If item lacks required use method
        :raises requests.exceptions.RequestException: If inventory update fails
        """
        mod = types.ModuleType(self.item_name)
        exec(self.source, mod.__dict__)
        getattr(mod, self.item_name)().use()
        status = Request(
            "PATCH",
            url=f"{os.getenv('API_URL')}:{os.getenv('API_PORT')}/v1/inventory/reduce/",
            data={
                "item_name": self.item_name,
                "item_owner": os.getenv("GITHUB_USER") or getpass.getuser(),
            },
        )()

    def __get_info(self):
        """Display information about an item by executing its string representation.
        :return: None
        :rtype: None
        :raises AttributeError: If item lacks required string method
        """
        mod = types.ModuleType(self.item_name)
        exec(self.source, mod.__dict__)
        print(f"You look at {self.item_name}. {getattr(mod, self.item_name)()}")


def cmd_use():
    """Command entry point for using an item.

    :return: None
    :rtype: None
    :raises SystemExit: If no item name provided
    """
    Usage(item_name=sys.argv[1])


def cmd_info():
    """Command entry point for inspecting an item.

    :return: None
    :rtype: None
    :raises SystemExit: If no item name provided
    """
    Usage(item_name=sys.argv[1], to_use=False)
