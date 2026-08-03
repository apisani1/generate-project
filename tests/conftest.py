"""Pytest configuration for template tests."""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import (
    Any,
    Generator,
)

import pytest

from pytest_cookies.plugin import Result
from tests.project_structure import (
    application_context,
    custom_context,
    library_context,
    supacode_context,
    uv_application_context,
    uv_custom_context,
    uv_library_context,
    uv_supacode_context,
)

# import sys
# from pathlib import Path


# THIS_DIR = Path(__file__).parent
# TESTS_DIR_PARENT = (THIS_DIR / "..").resolve()

# # ensure that `from tests ...` import statements work within the tests/ dir
# sys.path.insert(0, str(TESTS_DIR_PARENT))

TEMPLATE_DIR = str(Path("./src/generate_project/templates/poetry-template").resolve())
UV_TEMPLATE_DIR = str(Path("./src/generate_project/templates/uv-template").resolve())

print(f"Using template directory: {TEMPLATE_DIR}")
print(f"Using UV template directory: {UV_TEMPLATE_DIR}")


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


@pytest.fixture
def library_project(cookies: Result) -> Generator[Result, None, None]:
    """Create a library project using the template."""
    with bake_in_temp_dir(cookies, extra_context=library_context) as result:
        yield result


@pytest.fixture
def application_project(cookies: Result) -> Generator[Result, None, None]:
    """Create an application project using the template."""
    with bake_in_temp_dir(cookies, extra_context=application_context) as result:
        yield result


@pytest.fixture
def supacode_project(cookies: Result) -> Generator[Result, None, None]:
    """Create a project with the Supacode worktree config using the template."""
    with bake_in_temp_dir(cookies, extra_context=supacode_context) as result:
        yield result


# UV template fixtures


@contextmanager
def bake_uv_in_temp_dir(cookies: Result, **kwargs: Any) -> Generator[Result, None, None]:
    """Create a temporary directory and bake the UV cookiecutter template."""
    try:
        result = cookies.bake(template=UV_TEMPLATE_DIR, extra_context=kwargs.get("extra_context", {}))

        if result.exception:
            raise result.exception

        yield result

    except Exception as e:
        print(f"Error baking UV template: {e}")
        raise


@pytest.fixture
def uv_default_project(cookies: Result) -> Generator[Result, None, None]:
    """Create a default project using the UV template."""
    with bake_uv_in_temp_dir(cookies) as result:
        yield result


@pytest.fixture
def uv_custom_project(cookies: Result) -> Generator[Result, None, None]:
    """Create a customized project using the UV template."""
    with bake_uv_in_temp_dir(cookies, extra_context=uv_custom_context) as result:
        yield result


@pytest.fixture
def uv_library_project(cookies: Result) -> Generator[Result, None, None]:
    """Create a library project using the UV template."""
    with bake_uv_in_temp_dir(cookies, extra_context=uv_library_context) as result:
        yield result


@pytest.fixture
def uv_application_project(cookies: Result) -> Generator[Result, None, None]:
    """Create an application project using the UV template."""
    with bake_uv_in_temp_dir(cookies, extra_context=uv_application_context) as result:
        yield result


@pytest.fixture
def uv_supacode_project(cookies: Result) -> Generator[Result, None, None]:
    """Create a project with the Supacode worktree config using the UV template."""
    with bake_uv_in_temp_dir(cookies, extra_context=uv_supacode_context) as result:
        yield result
