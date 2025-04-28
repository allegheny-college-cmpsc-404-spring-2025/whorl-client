import re
import sys
import os
import importlib.util


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

    def __init__(self, filename, meta_file=None):
        """Initialize an ItemSpec instance.

        Args:
            filename (str): Path to the item's source file
            meta_file (str, optional): Path to metadata file if specified

        Note:
            Extracts modname from filename and sets CLI flags
        """
        self.filename = filename
        self.modname = filename.split(".")[0]
        self.modname = self.modname.split("/")[-1]
        self.__set_cli_flags()
        # get the absolute path of this item, especially if in a .pyz file
        self.absolute_path = self.get_absolute_path()

        # if meta_file is provided, load it
        if meta_file and os.path.exists(meta_file):
            self.load_metadata(meta_file)

    def load_metadata(self, meta_file):
        """Load metadata from a file.
        
        Args:
            meta_file (str): Path to the metadata file
            
        Returns:
            None
        """
        try:
            spec = importlib.util.spec_from_file_location("meta", meta_file)
            meta = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(meta)
            if hasattr(meta, "metadata") and isinstance(meta.metadata, dict):
                self.meta = meta.metadata
        except Exception as e:
            print(f"Error loading metadata from {meta_file}: {str(e)}")

    def get_absolute_path(self):
        """Get the absolute path of the item file.

        Resolves the absolute path of the item, specifically handling .pyz archives.

        Returns:
            str: Absolute path to the item file or containing .pyz
        """
        # check if any path in sys.path contains .pyz
        for path in sys.path:
            if '.pyz' in path and os.path.exists(path):
                return os.path.abspath(path)

        # check current module's __file__ attribute
        current_module = sys.modules.get(self.__class__.__module__)
        if current_module and hasattr(current_module, '__file__') and '.pyz' in current_module.__file__:
            pyz_path = current_module.__file__.split('.pyz')[0] + '.pyz'
            if os.path.exists(pyz_path):
                return os.path.abspath(pyz_path)

        # check sys.argv as fallback
        if len(sys.argv) > 0 and sys.argv[0].endswith('.pyz'):
            return os.path.abspath(sys.argv[0])

        # otherwise, return the normal path
        return os.path.abspath(self.filename)

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
