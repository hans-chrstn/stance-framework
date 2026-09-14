import argparse
import json
import sys
import os
from .validator import Validator


def cmd_init(args):
    package_id = args.package_id
    package_path = "package.json"

    if os.path.exists(package_path):
        print(f"Error: {package_path} already exists.", file=sys.stderr)
        sys.exit(1)

    initial_data = {
        "schemaVersion": 1,
        "packageId": package_id,
        "packageVersion": "0.1.0",
        "displayName": package_id,
        "trees": [
            {
                "treeId": "default",
                "displayName": "Default Tree",
                "defaultNode": "root",
                "nodes": [
                    {
                        "nodeId": "root",
                        "displayName": "Root Stance",
                        "parent": None,
                        "order": 0,
                        "unlock": {"mode": "always"},
                    }
                ],
            }
        ],
    }

    with open(package_path, "w", encoding="utf-8") as f:
        json.dump(initial_data, f, indent=2)
        f.write("\n")

    print(f"Initialized package {package_id} in {package_path}")


def cmd_validate(args):
    package_path = args.package_path

    if not os.path.exists(package_path):
        print(f"Error: file not found: {package_path}", file=sys.stderr)
        sys.exit(1)

    with open(package_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON syntax in {package_path}: {e}", file=sys.stderr)
            sys.exit(1)

    validator = Validator()
    is_valid = validator.validate_package(data)

    if not is_valid:
        print("Validation failed with the following diagnostics:", file=sys.stderr)
        for diag in validator.diagnostics:
            path_str = f" at {diag.path}" if diag.path else ""
            print(f"[{diag.level.upper()}] {diag.message}{path_str}", file=sys.stderr)
        sys.exit(1)
    else:
        print("Validation passed.")


def main():
    parser = argparse.ArgumentParser(description="Stances Framework authoring CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    init_parser = subparsers.add_parser("init", help="Initialize a new package")
    init_parser.add_argument(
        "package",
        nargs="?",
        const="package",
        help="The command target (must be 'package')",
    )
    init_parser.add_argument("package_id", help="The ID for the new package")

    # validate
    validate_parser = subparsers.add_parser("validate", help="Validate a package file")
    validate_parser.add_argument("package_path", help="Path to the package.json file")

    args = parser.parse_args()

    if args.command == "init":
        # Handle 'stancectl init package <package-id>'
        if args.package != "package":
            print("Usage: stancectl init package <package-id>", file=sys.stderr)
            sys.exit(1)
        cmd_init(args)
    elif args.command == "validate":
        cmd_validate(args)


if __name__ == "__main__":
    main()
