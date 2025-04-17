
import os
import sys
import yaml
import argparse
from datetime import datetime


def snake_to_camel(name):
    """Convert snake_case to CamelCase."""
    return ''.join(word.capitalize() for word in name.split('_'))


def create_item_directory(item_name):
    dir_name = item_name.lower().replace(" ", "_")
    os.makedirs(dir_name, exist_ok=True)
    print(f"Directory: {dir_name} {'created' if not os.path.exists(dir_name) else 'already exists'}")
    return dir_name


def create_meta_yaml(directory, metadata):
    meta_path = os.path.join(directory, "meta.yml")
    with open(meta_path, "w", encoding="utf-8") as file:
        yaml.dump(metadata, file, default_flow_style=False)
    print(f"Created meta.yml in {directory}")
    return meta_path


def create_item_module(directory, item_name, author, version):
    class_name = snake_to_camel(item_name)
    file_name = f"{item_name}.py"
    file_path = os.path.join(directory, file_name)

    template = f'''import os
import sys
from ItemSpec import ItemSpec

class {class_name}(ItemSpec):
    \"\"\"
    {item_name} implementation.

    Author: {author}
    Version: {version}
    \"\"\"
    def __init__(self, filename):
        dir_path = os.path.dirname(os.path.abspath(filename))
        meta_file = os.path.join(dir_path, "meta.yml")
        super().__init__(filename, meta_file)

    def __str__(self) -> str:
        if hasattr(self, 'meta') and self.meta and "description" in self.meta:
            return self.meta["description"]
        return f"A {{self.modname}} with no special properties."

    def use(self, **kwargs) -> None:
        nice_name = self.meta.get('nice_name', self.modname) if hasattr(self, 'meta') else self.modname
        print(f"You use the {{nice_name}}.")
'''

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(template)

    print(f"Created {file_name} in {directory}")
    return file_path


def create_init_file(directory, item_name):
    class_name = snake_to_camel(item_name)
    init_path = os.path.join(directory, "__init__.py")

    with open(init_path, "w", encoding="utf-8") as file:
        file.write(f"""# This file marks this directory as a Python package
from .{item_name} import {class_name}
""")

    print(f"Created __init__.py in {directory}")
    return init_path


def prompt_user_for_metadata():
    print("\n=== Whorl Item Creation Wizard ===\n")

    item_name = input("Item name (e.g. thermocube): ").strip().lower().replace(" ", "_")
    if not item_name:
        sys.exit("Error: Item name is required")

    author = input("Author/Username: ").strip()
    if not author:
        sys.exit("Error: Author is required")

    version = input("Version number [1.0.0]: ").strip() or "1.0.0"
    nice_name = input(f"Display name [{item_name.replace('_', ' ').title()}]: ").strip() or item_name.replace('_', ' ').title()
    description = input("Item description: ").strip()
    if not description:
        sys.exit("Error: Description is required")

    categories_input = input("Categories (comma-separated): ").strip()
    categories = [cat.strip() for cat in categories_input.split(",") if cat.strip()]

    price_input = input("Price (optional): ").strip()

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


def main():
    parser = argparse.ArgumentParser(description="Create a new item for the Whorl inventory system")
    parser.add_argument("--name", help="Item name")
    parser.add_argument("--author", help="Author name")
    parser.add_argument("--non-interactive", action="store_true", help="Run in non-interactive mode")
    args = parser.parse_args()

    if args.non_interactive:
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
        item_name, metadata = prompt_user_for_metadata()

    directory = create_item_directory(item_name)
    meta_path = create_meta_yaml(directory, metadata)
    module_path = create_item_module(directory, item_name, metadata["author"], metadata["version"])
    init_path = create_init_file(directory, item_name)

    print("\n=== Item Creation Complete ===")
    print(f"Item '{item_name}' created successfully!")
    print("Files created:")
    print(f"  - {meta_path}")
    print(f"  - {module_path}")
    print(f"  - {init_path}")

    print("\nNext steps:")
    print(f"1. Review and customize the item behavior in {module_path}")
    print(f"2. Add the item to your inventory with: get {item_name}/{item_name}.py")


if __name__ == "__main__":
    main()
