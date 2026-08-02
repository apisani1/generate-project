"""Example usage of {{ cookiecutter.project_name }}.

Run with:  make run
"""

import {{ cookiecutter.package_name }}


def main() -> None:
    """Demonstrate basic usage."""
    print("{{ cookiecutter.project_name }} version", {{ cookiecutter.package_name }}.__version__)
    print("Edit examples/main.py to show how to use this library.")


if __name__ == "__main__":
    main()
