"""Test basic template generation."""

import os
import subprocess

import pytest

from pytest_cookies.plugin import Result
from tests.project_structure import (
    application_context,
    custom_context,
)

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
    assert f"python = \"^{custom_context['python_min_version']}\"" in pyproject_content


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


def test_application_has_scripts_section(application_project: Result) -> None:
    """Test that application projects have [project.scripts] section."""
    pyproject_path = os.path.join(application_project.project_path, "pyproject.toml")
    with open(pyproject_path) as f:
        content = f.read()
    assert "[project.scripts]" in content, "Application should have [project.scripts]"
    project_name = application_context["project_name"]
    package_name = project_name.replace("-", "_").lower()
    assert f'{project_name} = "{package_name}.main:main"' in content


def test_library_has_no_scripts_section(library_project: Result) -> None:
    """Test that library projects do not have [project.scripts] section."""
    pyproject_path = os.path.join(library_project.project_path, "pyproject.toml")
    with open(pyproject_path) as f:
        content = f.read()
    assert "[project.scripts]" not in content, "Library should not have [project.scripts]"


def test_library_example_is_valid_python(library_project: Result) -> None:
    """Test that the rendered examples/main.py compiles (default_project drops examples/)."""
    example_path = os.path.join(library_project.project_path, "examples/main.py")
    try:
        subprocess.check_output(["python", "-m", "py_compile", example_path], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Python syntax error in {example_path}: {e.output}")


def test_poetry_keeps_the_venv_in_project(default_project: Result) -> None:
    """Without this, Poetry uses its global cache and the worktree venv handling is a no-op."""
    run_sh_path = os.path.join(default_project.project_path, "run.sh")
    with open(run_sh_path) as f:
        content = f.read()

    assert "export POETRY_VIRTUALENVS_IN_PROJECT=true" in content


def test_poetry_supacode_json_matches_uv(supacode_project: Result) -> None:
    """Both templates must ship byte-identical Supacode worktree config."""
    poetry_config = os.path.join(supacode_project.project_path, "supacode.json")
    with open(poetry_config) as f:
        content = f.read()

    assert '"setupScript" : "./run.sh worktree:setup"' in content
    assert '"archiveScript" : "./run.sh worktree:archive"' in content
    assert '"deleteScript" : "./run.sh worktree:delete"' in content


def test_poetry_run_uses_poetry(default_project: Result) -> None:
    """Test that the Poetry template's run function invokes poetry, not uv."""
    run_sh_path = os.path.join(default_project.project_path, "run.sh")
    with open(run_sh_path) as f:
        content = f.read()

    project_name = os.path.basename(default_project.project_path)
    assert f'poetry run {project_name} "$@"' in content, "Poetry template should run the console script via poetry"
