import os
import subprocess
from .ItemSpec import ItemSpec
import requests
from rich.console import Console
from rich.table import Table

from request import Request

console = Console()


class BackpackSpec(ItemSpec):
    """
    Represents a backpack item in the inventory system.

    This class allows for the storage of multiple items within the backpack,
    extending the inventory capacity.

    Attributes:
        capacity (int): The maximum number of items the backpack can hold. Defaults to 2.
        id (str): A unique identifier for the backpack instance.
    """

    capacity = 2

    def __init__(self, filename: str = "", id: str = "12345678"):
        """
        Initializes a BackpackSpec instance.

        Args:
            filename (str): The path to the item's source file.
            id (str): A unique identifier for the backpack. Defaults to "12345678".
        """
        super().__init__(filename)
        self.contents = []  # unused but needed for class to work
        self.id = id
        result = self.__setup_pack()

    def list_contents(self):
        """Lists the contents of the backpack. This is currently unused."""
        return self.contents

    def __setup_pack(self):
        """Sets up the backpack by making an API request to initialize its state."""
        try:
            response = Request(
                method="POST",
                url=f"{os.getenv('API_URL')}:{os.getenv('API_PORT')}/v1/omnipresence/",
                data={
                    "username": self.id,
                    "charname": self.id,
                    "working_dir": os.getcwd(),
                },
            )(raise_error=False)
            response.raise_for_status()
        except requests.HTTPError:
            response = Request(
                method="GET",
                url=f"{os.getenv('API_URL')}:{os.getenv('API_PORT')}/v1/omnipresence/",
                data={
                    "username": self.id,
                    "charname": self.id,
                    "working_dir": os.getcwd(),
                },
            )(raise_error=False)

        return response

    def __display(self):
        """Displays the contents of the backpack in a tabular format."""
        allowed = ["item_name", "item_qty", "item_bulk", "item_consumable"]
        api_request = Request(
            method="GET",
            url=f"{os.getenv('API_URL')}:{os.getenv('API_PORT')}/v1/inventory/list",
            data={"charname": self.id},
        )()

        context = api_request.json()

        total_volume = 0
        for item in context:
            total_volume += item["item_bulk"]

        table = Table(
            title=f"""{self.id}'s inventory
    ({total_volume}/10.0 spaces; {10.0 - total_volume} spaces remain)"""
        )
        table.add_column("Item name")
        table.add_column("Item count")
        table.add_column("Space Occupied")
        table.add_column("Consumable")

        for item in context:
            values = [str(item[field]) for field in item if field in allowed]
            table.add_row(*values)
        console.print(table)

    def __get(self, filename):
        """Retrieves an item from the inventory and stores it locally."""
        os.environ["INPACK"] = self.id
        subprocess.call(["get", filename])

    def __drop_item(self, item_name: str = "") -> None:
        """Drops a single item from the inventory and creates a local file."""
        os.environ["INPACK"] = self.id

        subprocess.call(["drop", item_name])

    def __use_item(self, item_name: str = "") -> None:
        """Uses an item from the inventory."""
        os.environ["INPACK"] = self.id
        subprocess.call(["use", item_name])

    def use(self):
        """Sets up a command-line interface for interacting with the backpack."""
        options = {"add", "drop", "use"}
        self.__display()
        mode = ""
        while mode not in options:
            mode = input(
                """To add an item: Type 'add' in terminal   
To drop and item: Type 'drop' in terminal
To use an item: Type 'use' in terminal\n Input: """
            )
            if mode not in options:
                console.print("\n[red][ERROR] [/red]Invalid input try again\n")
        if mode == "add":
            print("add")
            filename = input("Input Filename")
            self.__get(filename)
        elif mode == "drop":
            item_name = input("Input ItemName: ")
            self.__drop_item(item_name)
            print("drop")
        else:
            item_name = input("Input ItemName: ")
            self.__use_item(item_name)
