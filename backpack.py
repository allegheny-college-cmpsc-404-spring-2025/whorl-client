import os
from inventory.specs import BackpackSpec

class Backpack(BackpackSpec):
    """A custom backpack class extending BackpackSpec."""

    def __init__(self, capacity=5, id="example_id_here"):
        """Initialize the Backpack with a custom capacity and id."""
        super().__init__(__name__, id=id)
        self.capacity = capacity

    def __str__(self):
        """Return a string representation of the backpack."""
        self.display()
        return f"Custom Backpack (Capacity: {self.capacity}, ID: {self.id})"
