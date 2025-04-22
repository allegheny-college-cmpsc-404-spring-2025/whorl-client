from .ItemSpec import ItemSpec

class BackpackSpec(ItemSpec):
    """A class representing a backpack item in the inventory system.

    This class extends the inventory capacity by allowing items to be stored
    within the backpack itself.

    Attributes:
        capacity (int): Maximum number of items the backpack can hold.
        contents (list): List of items currently stored in the backpack.
    """

    capacity = 2

    def __init__(self, filename: str = ""):
        """Initialize a BackpackSpec instance.

        Args:
            filename (str): Path to the item's source file.
            capacity (int): Maximum number of items the backpack can hold.
        """
        super().__init__(filename)
        self.contents = []

    def add_item(self, item):
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

    def remove_item(self, item_name):
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

    def __str__(self):
        """Return a string representation of the backpack.

        Returns:
            str: Description of the backpack and its contents.
        """
        return f"Backpack (Capacity: {self.capacity}, Contents: {self.list_contents()})"
