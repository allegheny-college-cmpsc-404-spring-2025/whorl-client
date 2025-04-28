import os
import sys
import getpass
import argparse
from datetime import datetime
from inventory.Packager import Packager


def snake_to_camel(name):
    """Convert snake_case to CamelCase."""
    return ''.join(word.capitalize() for word in name.split('_'))


def create_item_directory(item_name):
    """Create a directory for the item."""
    dir_name = item_name.lower().replace(" ", "_")
    os.makedirs(dir_name, exist_ok=True)

    if os.path.exists(dir_name):
        status = "already exists"
    else:
        status = "created"

    print(f"Directory: {dir_name} {status}")
    return dir_name


def create_meta_py(directory, metadata):
    """Create a meta.py file in the item directory."""
    meta_path = os.path.join(directory, "meta.py")

    with open(meta_path, "w", encoding="utf-8") as file:
        file.write("# Auto-generated metadata for the item\n")
        file.write("metadata = {\n")
        for key, value in metadata.items():
            if isinstance(value, str):
                file.write(f'    "{key}": "{value}",\n')
            elif isinstance(value, list):
                file.write(f'    "{key}": {value},\n')
            else:
                file.write(f'    "{key}": {value},\n')
        file.write("}\n")

    print(f"Created meta.py in {directory}")
    return meta_path


def create_item_main(directory, item_name):
    """Create a __main__.py file for packaged item execution."""
    main_path = os.path.join(directory, "__main__.py")
    module_name = snake_to_camel(item_name)

    template = f'''# -*- coding: utf-8 -*-
import {module_name}
import meta

{module_name}.{module_name}()
'''

    with open(main_path, "w", encoding="utf-8") as file:
        file.write(template)

    print(f"Created __main__.py in {directory}")
    return main_path


def create_item_module(directory, item_name, author, version):
    """Create a Python module for the item."""
    class_name = item_name
    file_name = f"{snake_to_camel(item_name)}.py"
    file_path = os.path.join(directory, file_name)

    template = f'''import os
import sys
from inventory.specs import ItemSpec


class {snake_to_camel(class_name)}(ItemSpec):
    """
    {item_name}.

    Author: {author}
    Version: {version}
    """
    def __init__(self):
        dir_path = os.path.dirname(os.path.abspath(__name__))
        meta_file = os.path.join(dir_path, "meta.py")
        super().__init__(__name__, meta_file)

    def __str__(self) -> str:
        if hasattr(self, 'meta') and self.meta and "description" in self.meta:
            return self.meta["description"]
        return f"A {{self.modname}} with no special properties."
'''

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(template)

    print(f"Created {file_name} in {directory}")
    return file_path


def prompt_user_for_metadata():
    """Prompt the user for the metadata of the item."""
    print("\n=== Whorl Item Creation Wizard ===\n")

    # get required item information
    item_name = input("Item name (e.g. thermocube): ").strip().lower().replace(" ", "_")
    if not item_name:
        sys.exit("Error: Item name is required")

    # get username automatically
    author = getpass.getuser()

    # get optional item information with defaults
    version = input("Version number [1.0.0]: ").strip() or "1.0.0"
    default_nice_name = item_name.replace('_', ' ').title()
    nice_name = input(f"Display name [{default_nice_name}]: ").strip() or default_nice_name

    description = input("Item description: ").strip()
    if not description:
        sys.exit("Error: Description is required")

    # process the categories
    categories_input = input("Categories (comma-separated): ").strip()
    categories = [cat.strip() for cat in categories_input.split(",") if cat.strip()]

    # optional price
    price_input = input("Price (optional): ").strip()

    # build the metadata dictionary
    metadata = {
        "name": item_name,
        "nice_name": nice_name,
        "author": author,
        "version": version,
        "description": description,
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "categories": categories
    }

    if price_input:
        try:
            metadata["price"] = float(price_input)
        except ValueError:
            print("Warning: Invalid price format. Price will not be included.")

    return item_name, metadata


def cmd():
    """Command line entry point for creating a new item."""
    parser = argparse.ArgumentParser(description="Create a new item for the Whorl inventory system")
    parser.add_argument("--name", help="Item name")
    parser.add_argument("--author", help="Author name")
    parser.add_argument("--non-interactive", action="store_true", help="Run in non-interactive mode")
    parser.add_argument("--no-package", action="store_true", help="Skip creating .pyz package")
    args = parser.parse_args()

    if args.non_interactive:
        # non-interactive mode requires name and author
        if not args.name or not args.author:
            sys.exit("Error: --name and --author are required in non-interactive mode")

        item_name = args.name.lower().replace(" ", "_")
        metadata = {
            "name": item_name,
            "nice_name": item_name.replace("_", " ").title(),
            "author": args.author,
            "version": "1.0.0",
            "description": f"A {item_name} item",
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "categories": []
        }
    else:
        # interactive mode prompts for all metadata
        item_name, metadata = prompt_user_for_metadata()

    # create all necessary files
    directory = create_item_directory(item_name)
    meta_py_path = create_meta_py(directory, metadata)
    module_path = create_item_module(directory, item_name, metadata["author"], metadata["version"])
    main_path = create_item_main(directory, item_name)

    # show summary and next steps
    print("\n=== Item Creation Complete ===")
    print(f"Item '{item_name}' created successfully!")
    print("Files created:")
    print(f"  - {meta_py_path}")
    print(f"  - {module_path}")
    print(f"  - {main_path}")

    # package the item into a .pyz file unless --no-package is specified
    if not args.no_package:
        try:
            packager = Packager(directory)
            package_path = packager.package()
            print(f"\nPackaged item: {package_path}")
        except Exception as e:
            print(f"\nWarning: Could not package item: {str(e)}")
            print("You can manually package it later using the 'package' command.")

    print("\nNext steps:")
    if not args.no_package:
        print(f"1. Review and customize the item behavior in {module_path}")
        print(f"2. Add the item to your inventory with: get {package_path}")
    else:
        print(f"1. Review and customize the item behavior in {module_path}")
        print(f"2. Package the item with: package {directory}")
        print(f"3. Add the item to your inventory with: get {item_name}/{item_name}.py")
