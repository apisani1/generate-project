"""Test the project structure is as expected."""

import os
import re

from pytest_cookies.plugin import Result
from tests.project_structure import (
    custom_context,
    docs_files,
    expected_files,
    github_workflow_files,
)


def path_in_output(result: Result, *paths: str) -> str:
    """Join paths with the output directory."""
    return os.path.join(result.project_path, *paths)


def test_project_structure(default_project: Result) -> None:
    """Test that all required files and directories exist."""

    for path in expected_files:
        assert os.path.exists(path_in_output(default_project, path)), f"Missing file or directory: {path}"

    # Package-specific file with dynamic package name
    package_name = os.path.basename(default_project.project_path).replace("-", "_").lower()
    assert os.path.exists(
        path_in_output(default_project, f"src/{package_name}/__init__.py")
    ), f"Missing package init file: src/{package_name}/__init__.py"


def test_src_structure(default_project: Result) -> None:
    """Test that src directory has the correct structure."""
    # Get package name from project directory
    package_name = os.path.basename(default_project.project_path).replace("-", "_").lower()

    # Check src directory structure
    assert os.path.isdir(path_in_output(default_project, "src")), "Missing src directory"
    assert os.path.isdir(
        path_in_output(default_project, f"src/{package_name}")
    ), f"Missing package directory: src/{package_name}"
    assert os.path.exists(
        path_in_output(default_project, f"src/{package_name}/__init__.py")
    ), "Missing __init__.py in package directory"

    # Check __init__.py content
    init_path = path_in_output(default_project, f"src/{package_name}/__init__.py")
    with open(init_path) as f:
        init_content = f.read()

    assert "__version__" in init_content, "Missing __version__ in __init__.py"


def test_documentation_structure(default_project: Result) -> None:
    """Test that documentation directory has the correct structure."""
    # Check docs directory structure
    for path in docs_files:
        assert os.path.exists(
            path_in_output(default_project, path)
        ), f"Missing documentation file or directory: {path}"

    # Check docs content
    with open(path_in_output(default_project, "docs/index.md")) as f:
        index_content = f.read()

    assert "# my-project" in index_content, "Project name not found in index.md"

    with open(path_in_output(default_project, "docs/conf.py")) as f:
        conf_content = f.read()

    assert "sphinx" in conf_content, "Sphinx configuration missing in conf.py"
    assert "extensions" in conf_content, "Extensions configuration missing in conf.py"


def test_github_workflows(default_project: Result) -> None:
    """Test that GitHub workflow files exist and have expected content."""
    # Check GitHub workflow files
    for path in github_workflow_files:
        assert os.path.exists(path_in_output(default_project, path)), f"Missing GitHub workflow file: {path}"

    # Check workflow content
    with open(path_in_output(default_project, ".github/workflows/docs.yml")) as f:
        docs_workflow = f.read()

    assert "Documentation" in docs_workflow, "Missing workflow name in docs.yml"
    assert "actions/checkout" in docs_workflow, "Missing checkout action in docs.yml"

    with open(path_in_output(default_project, ".github/workflows/release.yml")) as f:
        release_workflow = f.read()

    assert "Release" in release_workflow, "Missing workflow name in release.yml"
    assert "tags: ['v*']" in release_workflow, "Missing tag trigger in release.yml"

    with open(path_in_output(default_project, ".github/workflows/tests.yml")) as f:
        tests_workflow = f.read()

    assert "Tests" in tests_workflow, "Missing workflow name in tests.yml"
    assert "workflow_call:" in tests_workflow, "Missing workflow_call trigger in tests.yml"

    with open(path_in_output(default_project, ".github/workflows/update_rtd.yml")) as f:
        update_rtd_workflow = f.read()

    assert "Update ReadTheDocs" in update_rtd_workflow, "Missing workflow name in update_rtd.yml"
    assert "workflow_dispatch:" in update_rtd_workflow, "Missing workflow_dispatch trigger in update_rtd.yml"


def test_pyproject_toml_content(default_project: Result) -> None:
    """Test that pyproject.toml contains expected content."""
    # Check pyproject.toml content
    with open(path_in_output(default_project, "pyproject.toml")) as f:
        pyproject_content = f.read()

    # Basic checks
    assert "poetry-core" in pyproject_content, "Missing poetry-core in pyproject.toml"
    assert "tool.poetry" in pyproject_content, "Missing tool.poetry section in pyproject.toml"
    assert 'name = "my-project"' in pyproject_content, "Project name not found in pyproject.toml"

    # Check tool configuration sections
    assert "tool.black" in pyproject_content, "Missing tool.black in pyproject.toml"
    assert "tool.flake8" in pyproject_content, "Missing tool.flake8 in pyproject.toml"
    assert "tool.mypy" in pyproject_content, "Missing tool.mypy in pyproject.toml"
    assert "tool.isort" in pyproject_content, "Missing tool.isort in pyproject.toml"


def test_makefile_content(default_project: Result) -> None:
    """Test that Makefile contains expected targets."""
    with open(path_in_output(default_project, "Makefile")) as f:
        makefile_content = f.read()

    # Check for common make targets
    expected_targets = ["install", "format", "lint", "test", "docs", "build", "publish"]

    for target in expected_targets:
        assert re.search(rf"{target}\s*:", makefile_content), f"Missing '{target}' target in Makefile"


def test_custom_project_parameters(custom_project: Result) -> None:
    """Test that custom project parameters are properly applied."""
    # Check custom project name in pyproject.toml
    with open(path_in_output(custom_project, "pyproject.toml")) as f:
        pyproject_content = f.read()

    assert (
        custom_context["project_name"] in pyproject_content in pyproject_content
    ), "Custom project name not found in pyproject.toml"
    assert custom_context["author_name"] in pyproject_content, "Custom author name not found in pyproject.toml"
    assert custom_context["email"] in pyproject_content, "Custom email not found in pyproject.toml"
    assert custom_context["version"] in pyproject_content, "Custom version not found in pyproject.toml"

    # Check custom project description in README
    with open(path_in_output(custom_project, "README.md")) as f:
        readme_content = f.read()

    assert custom_context["description"] in readme_content, "Custom description not found in README.md"

    # Check that package directory is created with correct name
    package_name = custom_context["project_name"].replace("-", "_").lower()
    assert os.path.isdir(
        path_in_output(custom_project, f"src/{package_name}")
    ), f"Custom package directory not found: src/{package_name}"
