import os

from Instance import Instance

from .ItemSpec import ItemSpec
import requests
from rich.console import Console
from rich.table import Table

from request import Request

console = Console()


class BackpackSpec(ItemSpec):
    """A class representing a backpack item in the inventory system.

    This class extends the inventory capacity by allowing items to be stored
    within the backpack itself.

    Attributes:
        capacity (int): Maximum number of items the backpack can hold.
        contents (list): List of items currently stored in the backpack.
    """

    capacity = 2

    def __init__(self, filename: str = "", id: str = "12345678"):
        """Initialize a BackpackSpec instance.

        Args:
            filename (str): Path to the item's source file.
            capacity (int): Maximum number of items the backpack can hold.
        """
        super().__init__(filename)
        self.contents = []
        self.id = id
        result = self.__setup_pack()
        print(result)

    def __setup_pack(self):
        print(self.id)
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

    def __add_item(self, item):
        """Add an item to the backpack.

        Args:
            item (ItemSpec): The item to add to the backpack.

        Returns:
            bool: True if the item was added, False if the backpack is full.
        """
        if len(self.contents) < self.capacity:
            self.contents.append(item)
            return True
        print("Backpack is full!")
        return False

    def __remove_item(self, item_name):
        """Remove an item from the backpack by name.

        Args:
            item_name (str): The name of the item to remove.

        Returns:
            ItemSpec: The removed item, or None if not found.
        """
        for item in self.contents:
            if item.modname == item_name:
                self.contents.remove(item)
                return item
        print(f"Item '{item_name}' not found in the backpack!")
        return None

    def list_contents(self):
        """List the contents of the backpack.

        Returns:
            list: A list of item names currently in the backpack.
        """
        return [item.modname for item in self.contents]

    def __display(self):
        """Return a string representation of the backpack.

        Returns:
            str: Description of the backpack and its contents.
        """
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

    def __get(self):
        instance = Instance()
        response = Request(
            method="POST",
            url=f"{os.getenv('API_URL')}:{os.getenv('API_PORT')}/v1/inventory/add/",
            data=instance.transmit,
            files={"item_binary": instance.binary},
        )()
        if response.status_code == 409:
            context = response.json()
            print(context["error"])

    def use(self):
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
        elif mode == "drop":
            print("drop")
        else:
            print("use")
