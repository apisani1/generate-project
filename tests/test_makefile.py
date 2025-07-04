"""Test Makefile targets in the generated project."""

import os
import subprocess

import pytest

from pytest_cookies.plugin import Result
from tests.conftest import inside_dir


def test_makefile_exists(default_project: Result) -> None:
    """Test that the Makefile exists."""
    assert os.path.exists(os.path.join(default_project.project_path, "Makefile"))


def test_makefile_help(default_project: Result) -> None:
    """Test that 'make help' runs successfully."""
    with inside_dir(default_project.project_path):
        try:
            result = subprocess.run(["make", "help"], check=True, capture_output=True, text=True)

            # Check that common targets are listed in help
            help_text = result.stdout
            expected_targets = ["install", "format", "lint", "test", "docs", "build", "publish"]
            for target in expected_targets:
                assert target in help_text, f"Target '{target}' not found in make help"
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Failed to execute make help: {e.stderr}")


def test_makefile_clean(default_project: Result) -> None:
    """Test that 'make clean' runs successfully."""
    with inside_dir(default_project.project_path):
        # Create some files/dirs that should be cleaned
        os.makedirs("dist", exist_ok=True)
        os.makedirs(".pytest_cache", exist_ok=True)

        try:
            subprocess.run(["make", "clean"], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Failed to execute make clean: {e.stderr}")

        assert not os.path.exists("dist")
        assert not os.path.exists(".pytest_cache")


def test_makefile_check(default_project: Result) -> None:
    """Test that 'make check' runs successfully."""
    with inside_dir(default_project.project_path):
        subprocess.run(["make", "format"], check=False, capture_output=True, text=True)
        try:
            subprocess.run(["make", "check"], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Failed to execute make check: {e.stderr}")
