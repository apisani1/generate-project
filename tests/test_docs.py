"""Test documentation generation in the project."""

import os
import subprocess

import pytest

from pytest_cookies.plugin import Result
from tests.conftest import inside_dir
from tests.project_structure import application_context, library_context


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


def test_application_docs_content(application_project: Result) -> None:
    """Test that application docs have correct content."""
    index_path = os.path.join(application_project.project_path, "docs/index.md")
    with open(index_path) as f:
        content = f.read()
    assert "application" in content, "Docs should reference application"
    assert "{{ cookiecutter" not in content, "No unrendered templates"
    # Application-specific content - CLI quick start
    project_name = application_context["project_name"]
    package_name = project_name.replace("-", "_").lower()
    assert f"pip install {project_name}" in content, "Should have pip install command"
    assert package_name in content, "Should have CLI command"


def test_library_docs_content(library_project: Result) -> None:
    """Test that library docs have correct content."""
    index_path = os.path.join(library_project.project_path, "docs/index.md")
    with open(index_path) as f:
        content = f.read()
    assert "library" in content, "Docs should reference library"
    assert "{{ cookiecutter" not in content, "No unrendered templates"
    # Library-specific content
    package_name = library_context["project_name"].replace("-", "_").lower()
    assert f"from {package_name} import Example" in content, "Should have Example import"
