import os
import sys
import argparse
import zipapp
import shutil
import tempfile
import importlib.util
from typing import List, Dict, Optional
import traceback


class Packager:
    """Converts an item directory into a .pyz package"""

    @staticmethod
    def snake_to_camel(name: str) -> str:
        """Convert snake_case to CamelCase (to match the Create module's style)"""
        return ''.join(word.capitalize() for word in name.split('_'))

    def __init__(self, directory: str, output_dir: Optional[str] = None):
        """
        Initialize the packager for an item directory

        Args:
            directory: Path to the directory containing the item
            output_dir: Where to place the packaged file (default: current directory)
        """
        # strip the trailing slashes from the directory path (idk if this is ideal in the longterm)
        directory = directory.rstrip('/\\')
        self.directory = os.path.abspath(directory)
        self.module_name = self.snake_to_camel(os.path.basename(directory))
        self.output_dir = output_dir or os.getcwd()
        self.pyz_path = os.path.join(self.output_dir, f"{self.module_name}.pyz")
        # this is for staging files before packaging
        self.temp_dir = None

    def _validate_structure(self) -> None:
        """Ensure directory has required files and valid content"""
        required_files = [
            "meta.py",
            f"{self.module_name}.py"
        ]

        # Check for required files
        missing = [f for f in required_files
                   if not os.path.exists(os.path.join(self.directory, f))]

        if missing:
            raise FileNotFoundError(
                f"Missing required files in {self.directory}: {', '.join(missing)}"
            )

        # validate meta.py can be imported and has metadata
        meta_path = os.path.join(self.directory, "meta.py")
        try:
            spec = importlib.util.spec_from_file_location("meta", meta_path)
            meta = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(meta)

            if not hasattr(meta, "metadata") or not isinstance(meta.metadata, dict):
                raise ValueError(f"meta.py must define a 'metadata' dictionary")
        except Exception as e:
            raise ValueError(f"Invalid meta.py file: {str(e)}")

        # validate main module can be imported
        module_path = os.path.join(self.directory, f"{self.module_name}.py")
        try:
            spec = importlib.util.spec_from_file_location(self.module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            class_exists = hasattr(module, self.module_name)
            if not class_exists:
                raise ValueError(f"Module must contain a class named '{self.module_name}'")
        except Exception as e:
            raise ValueError(f"Invalid module file: {str(e)}")

    def _prepare_staging_area(self) -> None:
        """Create a temporary directory and copy files for packaging"""
        self.temp_dir = tempfile.mkdtemp()

        # copy all files from source directory
        for item in os.listdir(self.directory):
            src_path = os.path.join(self.directory, item)
            dst_path = os.path.join(self.temp_dir, item)

            if os.path.isfile(src_path):
                shutil.copy2(src_path, dst_path)
            elif os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)

    def _add_entrypoint(self) -> None:
        """Add __main__ guard to module file if missing"""
        module_path = os.path.join(self.temp_dir, f"{self.module_name}.py")
        entrypoint_code = f"\n\nif __name__ == '__main__':\n    {self.module_name}().use()"

        with open(module_path, "r", encoding="utf-8") as f:
            content = f.read()

        # only add if not already present (using more robust check)
        if f"if __name__ == '__main__'" not in content:
            with open(module_path, "a", encoding="utf-8") as f:
                f.write(entrypoint_code)

    def _get_python_executable(self) -> str:
        """Get the appropriate Python executable path for the current system"""
        # use sys.executable
        return sys.executable

    def _cleanup(self) -> None:
        """Remove temporary directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None

    def package(self, force: bool = False) -> str:
        """
        Create the .pyz archive

        Args:
            force: If True, overwrite existing package with same name

        Returns:
            Absolute path to the created package
        """
        try:
            # ensure output directory exists
            os.makedirs(self.output_dir, exist_ok=True)

            # check if output file already exists
            if os.path.exists(self.pyz_path) and not force:
                raise FileExistsError(
                    f"Output file {self.pyz_path} already exists. Use force=True to overwrite."
                )

            # validate the source directory
            self._validate_structure()

            # create a staging area
            self._prepare_staging_area()

            # add entrypoint if needed
            self._add_entrypoint()

            # Get the Python interpreter path
            python_executable = self._get_python_executable()

            # creare the pyz archive
            zipapp.create_archive(
                source=self.temp_dir,
                target=self.pyz_path,
                main=f"{self.module_name}:{self.module_name}",
                interpreter=python_executable,
                compressed=True
            )

            return self.pyz_path

        except Exception as e:
            # re-raise with more context
            raise RuntimeError(f"Failed to package {self.directory}: {str(e)}") from e
        finally:
            # always clean up temporary files!
            self._cleanup()


def cmd():
    """Command line interface for packaging"""
    parser = argparse.ArgumentParser(
        description="Convert items into portable .pyz packages"
    )
    parser.add_argument(
        "directory",
        help="Directory containing the item to package"
    )
    parser.add_argument(
        "-o", "--output-dir",
        help="Directory where the package will be saved"
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Overwrite existing package if it exists"
    )

    args = parser.parse_args()

    try:
        packager = Packager(args.directory, args.output_dir)
        output_path = packager.package(force=args.force)
        print(f"Successfully created package: {output_path}")
    except Exception as e:
        print(f"Error: {str(e)}")
