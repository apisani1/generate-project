#!/usr/bin/env python3
"""Post-generation hook for cookiecutter template."""

import os

PROJECT_TYPE = "{{ cookiecutter.project_type }}"
PACKAGE_NAME = "{{ cookiecutter.package_name }}"


def remove_file(filepath: str) -> None:
    """Remove a file if it exists."""
    if os.path.exists(filepath):
        os.remove(filepath)


def main() -> None:
    """Run post-generation tasks."""
    # For library projects, remove the main.py CLI entry point
    if PROJECT_TYPE == "library":
        main_py_path = os.path.join("src", PACKAGE_NAME, "main.py")
        remove_file(main_py_path)


if __name__ == "__main__":
    main()
