"""Pytest configuration for template tests."""

import os
from contextlib import contextmanager
from typing import (
    Any,
    Generator,
)

import pytest

from pytest_cookies.plugin import Result
from tests.project_structure import custom_context


# import sys
# from pathlib import Path


# THIS_DIR = Path(__file__).parent
# TESTS_DIR_PARENT = (THIS_DIR / "..").resolve()

# # ensure that `from tests ...` import statements work within the tests/ dir
# sys.path.insert(0, str(TESTS_DIR_PARENT))

TEMPLATE_DIR = "/Users/antonio/Desktop/AI/MyCode/generate-project/src/generate_project/templates/poetry-template"

print(f"Using template directory: {TEMPLATE_DIR}")


@contextmanager
def inside_dir(dirpath: str) -> Generator[None, None, None]:
    """Execute code from inside the given directory."""
    old_path = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)


@contextmanager
def bake_in_temp_dir(cookies: Result, **kwargs: Any) -> Generator[Result, None, None]:
    """Create a temporary directory and bake a cookiecutter template."""
    try:
        result = cookies.bake(template=TEMPLATE_DIR, extra_context=kwargs.get("extra_context", {}))

        if result.exception:
            raise result.exception

        yield result

    except Exception as e:
        # Log any exceptions for debugging
        print(f"Error baking template: {e}")
        raise


@pytest.fixture
def default_project(cookies: Result) -> Generator[Result, None, None]:
    """Create a default project using the template."""
    with bake_in_temp_dir(cookies) as result:
        yield result


@pytest.fixture
def custom_project(cookies: Result) -> Generator[Result, None, None]:
    """Create a customized project using the template."""

    with bake_in_temp_dir(cookies, extra_context=custom_context) as result:
        yield result
