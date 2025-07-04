"""Test basic template generation."""

import os
import subprocess

import pytest

from pytest_cookies.plugin import Result
from tests.project_structure import custom_context


def test_project_generation(default_project: Result) -> None:
    """Test that project is generated and renders correctly."""
    assert default_project.exit_code == 0
    assert default_project.exception is None
    assert default_project.project_path.name == "my-project"
    assert os.path.isdir(default_project.project_path)


def test_custom_project_generation(custom_project: Result) -> None:
    """Test generation with custom parameters."""
    assert custom_project.exit_code == 0
    assert custom_project.exception is None
    assert custom_project.project_path.name == custom_context["project_name"]

    # Check that variables were substituted correctly
    readme_path = os.path.join(custom_project.project_path, "README.md")
    assert os.path.exists(readme_path), f"README.md file not found at {readme_path}"

    with open(readme_path) as f:
        readme_content = f.read()
    assert (
        custom_context["project_name"] in readme_content
    ), f"Project name not found in README.md: {readme_content[:100]}..."

    pyproject_path = os.path.join(custom_project.project_path, "pyproject.toml")
    assert os.path.exists(pyproject_path), f"pyproject.toml file not found at {pyproject_path}"

    with open(pyproject_path) as f:
        pyproject_content = f.read()
        print(f"pyproject.toml content: {pyproject_content}...")  # Print first 100 characters for debugging
    assert f"name = \"{custom_context['project_name']}\"" in pyproject_content
    assert f"version = \"{custom_context['version']}\"" in pyproject_content
    assert f"python = \"{custom_context['python_version']}\"" in pyproject_content


def test_python_syntax(default_project: Result) -> None:
    """Test that Python files are valid syntax."""
    for root, _, files in os.walk(default_project.project_path):
        for file_name in files:
            if file_name.endswith(".py"):
                file_path = os.path.join(root, file_name)
                try:
                    subprocess.check_output(["python", "-m", "py_compile", file_path], stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as e:
                    pytest.fail(f"Python syntax error in {file_path}: {e.output}")
