import os
from inventory.specs import BackpackSpec

class Backpack(BackpackSpec):  # Capitalized class name
    """A custom backpack class extending BackpackSpec."""

    def __init__(self, capacity=5):
        """Initialize the Backpack with a custom capacity."""
        super().__init__(__name__)
        self.capacity = capacity  # Set the capacity of the backpack

    def __str__(self):
        """Return a string representation of the backpack."""
        return f"Custom Backpack (Capacity: {self.capacity}, Contents: {self.list_contents()})"
