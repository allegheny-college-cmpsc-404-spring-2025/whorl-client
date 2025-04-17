import os
from request import Request

import requests

import os
import sys
import base64
import pennant
import requests
import getpass

from dotenv import load_dotenv

from rich.table import Table
from rich.console import Console
from request import Request

load_dotenv()


def list():
    """Display a formatted table of the user's inventory contents.

    Shows item names, quantities, space occupied, and whether items are consumable.
    Also displays total inventory space used and remaining.

    :return: None - Prints inventory table to console
    :rtype: None
    :raises requests.exceptions.RequestException: If the inventory API request fails
    """
    allowed = ["item_name", "item_qty", "item_bulk", "item_consumable"]

    api_request = Request(
        method="GET",
        url=f"{os.getenv('API_URL')}:{os.getenv('API_PORT')}/v1/inventory/list",
        data={"charname": "packpack_test"},
    )()

    context = api_request.json()

    total_volume = 0
    for item in context:
        total_volume += item["item_bulk"]

    table = Table(
        title=f"""Packs's inventory
({total_volume}/10.0 spaces; {10.0 - total_volume} spaces remain)"""
    )
    table.add_column("Item name")
    table.add_column("Item count")
    table.add_column("Space Occupied")
    table.add_column("Consumable")

    for item in context:
        values = [str(item[field]) for field in item if field in allowed]
        table.add_row(*values)

    Console().print(table)


def main():
    response = Request(
        method="POST",
        url=f"{os.getenv('API_URL')}:{os.getenv('API_PORT')}/v1/omnipresence/",
        data={
            "username": "packpack_test",
            "charname": "packpack_test",
            "working_dir": os.getcwd(),
        },
    )()

    if response.status_code == 201:
        list()
    else:
        print("No backpack found")


if __name__ == "__main__":
    main()
