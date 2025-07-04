"""Test documentation generation in the project."""

import os
import subprocess

import pytest

from pytest_cookies.plugin import Result
from tests.conftest import inside_dir


def test_docs_generation(default_project: Result) -> None:
    """Test that documentation can be generated with Sphinx."""
    # This test might be slow, so we'll make it explicit
    if os.environ.get("SKIP_SLOW_TESTS"):
        pytest.skip("Skipping slow documentation test")

    with inside_dir(default_project.project_path):
        try:
            subprocess.run(["poetry", "install", "--with", "docs"], check=True, capture_output=True)

            # Generate API documentation first
            subprocess.run(["make", "docs-api"], check=True, capture_output=True, text=True)

            # Then build the full documentation
            subprocess.run(["make", "docs"], capture_output=True, check=True, text=True)

            # Check that html was generated
            assert os.path.exists("docs/_build/html/index.html")
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Documentation generation failed: {e.stderr}")
