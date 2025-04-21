import os

from inventory.specs import BackpackSpec

class Backpack(BackpackSpec):
    def __init__(self):
        """Constructor"""
        super().__init__(__name__, capacity=10)  # Set capacity to 10 or any desired value

    def __str__(self):
        return f"My custom backpack with capacity {self.capacity}."
