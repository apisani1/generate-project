#!/usr/bin/env python3
"""Post-generation hook for cookiecutter template."""

import os
import shutil

PROJECT_TYPE = "{{ cookiecutter.project_type }}"
PACKAGE_NAME = "{{ cookiecutter.package_name }}"
INCLUDE_SUPACODE = "{{ cookiecutter.include_supacode }}"


def remove_file(filepath: str) -> None:
    """Remove a file if it exists."""
    if os.path.exists(filepath):
        os.remove(filepath)


def remove_dir(dirpath: str) -> None:
    """Remove a directory tree if it exists."""
    if os.path.isdir(dirpath):
        shutil.rmtree(dirpath)


def main() -> None:
    """Run post-generation tasks."""
    if PROJECT_TYPE == "library":
        # Libraries have no CLI entry point; `make run` falls back to examples/main.py
        main_py_path = os.path.join("src", PACKAGE_NAME, "main.py")
        remove_file(main_py_path)
    else:
        # Applications run via their console script, so the example is redundant
        remove_dir("examples")

    # Supacode worktree lifecycle config is opt-in via `generate --supacode`
    if INCLUDE_SUPACODE != "yes":
        remove_file("supacode.json")


if __name__ == "__main__":
    main()
