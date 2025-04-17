import re
import sys
import os
import yaml


class ItemSpec:
    """Base class for defining item specifications in the inventory system.
    
    This class provides the foundational attributes and methods that all inventory
    items must implement. It handles basic item properties, CLI flag parsing, and
    default behaviors.

    Attributes:
        volume (int): Space taken up by the item in inventory. Defaults to 1.
        version (str): Version string of the item spec. Defaults to "1.0.0".
        actions (dict): Available actions for this item. Defaults to empty dict.
        consumable (bool): Whether item is consumed on use. Defaults to True.
        filename (str): Path to the item's source file
        modname (str): Module name extracted from filename
    """

    volume = 1
    version = "1.0.0"
    actions = {}
    consumable = True

    def __init__(self, filename, meta_file):
        """Initialize an ItemSpec instance.

        Args:
            filename (str): Path to the item's source file

        Note:
            Extracts modname from filename and sets CLI flags
        """
        self.filename = filename
        self.modname = filename.split(".")[0]
        self.modname = self.modname.split("/")[-1]
        self.__set_cli_flags()

        # If meta_file is not provided, try to find it in the standard location
        if not os.path.exists(meta_file):
            raise FileNotFoundError(f"Meta file {meta_file} not found.")

        # load the meta file and open it
        try:
            with open(meta_file, "r", encoding="utf-8") as file:
                self.meta = yaml.safe_load(file)
        except Exception as e:
            raise RuntimeError(f"Failed to load meta file {meta_file}: {e}") from e

    def __set_cli_flags(self):
        """Parse command line arguments and set them as object attributes.
    
        Extracts command line flags using regex pattern matching and sets them
        as instance attributes. Supports both single (-) and double dash (--)
        flag formats.

        Example:
            With sys.argv = ["script.py", "--flag", "value"]
            Results in: self.flag = "value"
        """
        flags = re.findall(
            r"((?<![a-z])-{1,2}[a-z0-9]+)(?:\s)([a-zA-Z0-9_]+)?",
            ' '.join(sys.argv[1:])
        )
        for arg, val in flags:
            arg = arg.replace("-","")
            setattr(self, arg, val)

    def __str__(self) -> str:
        """Return string representation of the item.

        Returns:
            str: Generic description including the item's module name
        """
        return f"""This particular {self.modname} isn't that special."""

    def use(self, **kwargs) -> None:
        """Attempt to use the item.
        
        Args:
            kwargs: Arbitrary keyword arguments for item usage

        Returns:
            None: Prints a generic usage message
        """
        print(f"You try the {self.__module__}, but it doesn't do anything.")
