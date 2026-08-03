"""Test UV template generation."""

import os
import subprocess

import pytest

from pytest_cookies.plugin import Result
from tests.project_structure import (
    uv_application_context,
    uv_custom_context,
)

def test_uv_project_generation(uv_default_project: Result) -> None:
    """Test that UV project is generated and renders correctly."""
    assert uv_default_project.exit_code == 0
    assert uv_default_project.exception is None
    assert uv_default_project.project_path.name == "my-project"
    assert os.path.isdir(uv_default_project.project_path)


def test_uv_custom_project_generation(uv_custom_project: Result) -> None:
    """Test UV generation with custom parameters."""
    assert uv_custom_project.exit_code == 0
    assert uv_custom_project.exception is None
    assert uv_custom_project.project_path.name == uv_custom_context["project_name"]

    # Check that variables were substituted correctly
    readme_path = os.path.join(uv_custom_project.project_path, "README.md")
    assert os.path.exists(readme_path)

    with open(readme_path) as f:
        readme_content = f.read()
    assert uv_custom_context["project_name"] in readme_content

    pyproject_path = os.path.join(uv_custom_project.project_path, "pyproject.toml")
    assert os.path.exists(pyproject_path)

    with open(pyproject_path) as f:
        pyproject_content = f.read()
    assert f"name = \"{uv_custom_context['project_name']}\"" in pyproject_content
    assert f"version = \"{uv_custom_context['version']}\"" in pyproject_content
    assert f"requires-python = \">={uv_custom_context['python_min_version']}\"" in pyproject_content


def test_uv_pyproject_format(uv_default_project: Result) -> None:
    """Test that UV pyproject.toml uses hatchling and PEP 621 format."""
    pyproject_path = os.path.join(uv_default_project.project_path, "pyproject.toml")
    with open(pyproject_path) as f:
        content = f.read()

    # Build system should use hatchling
    assert "hatchling" in content, "UV template should use hatchling build backend"
    assert "[build-system]" in content

    # Should use PEP 621 [project] section, not [tool.poetry]
    assert "[project]" in content, "UV template should use [project] section"
    assert "[tool.poetry]" not in content, "UV template should not have [tool.poetry]"

    # Should have dependency-groups
    assert "[dependency-groups]" in content, "UV template should use [dependency-groups]"

    # Should have tool configs
    assert "[tool.black]" in content
    assert "[tool.mypy]" in content
    assert "[tool.isort]" in content


def test_uv_run_sh_commands(uv_default_project: Result) -> None:
    """Test that run.sh uses UV commands instead of Poetry."""
    run_sh_path = os.path.join(uv_default_project.project_path, "run.sh")
    with open(run_sh_path) as f:
        content = f.read()

    assert "uv sync" in content, "run.sh should use 'uv sync'"
    assert "uv run" in content, "run.sh should use 'uv run'"
    assert "uv build" in content, "run.sh should use 'uv build'"
    assert "uv publish" in content, "run.sh should use 'uv publish'"


def test_uv_python_syntax(uv_default_project: Result) -> None:
    """Test that Python files in UV template are valid syntax."""
    for root, _, files in os.walk(uv_default_project.project_path):
        for file_name in files:
            if file_name.endswith(".py"):
                file_path = os.path.join(root, file_name)
                try:
                    subprocess.check_output(["python", "-m", "py_compile", file_path], stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as e:
                    pytest.fail(f"Python syntax error in {file_path}: {e.output}")


def test_uv_application_has_scripts_section(uv_application_project: Result) -> None:
    """Test that UV application projects have [project.scripts] section."""
    pyproject_path = os.path.join(uv_application_project.project_path, "pyproject.toml")
    with open(pyproject_path) as f:
        content = f.read()
    assert "[project.scripts]" in content, "Application should have [project.scripts]"
    project_name = uv_application_context["project_name"]
    package_name = project_name.replace("-", "_").lower()
    assert f'{project_name} = "{package_name}.main:main"' in content


def test_uv_library_has_no_scripts_section(uv_library_project: Result) -> None:
    """Test that UV library projects do not have [project.scripts] section."""
    pyproject_path = os.path.join(uv_library_project.project_path, "pyproject.toml")
    with open(pyproject_path) as f:
        content = f.read()
    assert "[project.scripts]" not in content, "Library should not have [project.scripts]"


def test_uv_application_has_main_py(uv_application_project: Result) -> None:
    """Test that UV application projects have main.py."""
    package_name = uv_application_context["project_name"].replace("-", "_").lower()
    main_py_path = os.path.join(uv_application_project.project_path, f"src/{package_name}/main.py")
    assert os.path.exists(main_py_path), "Application should have main.py"


def test_uv_library_has_no_main_py(uv_library_project: Result) -> None:
    """Test that UV library projects do not have main.py."""
    from tests.project_structure import uv_library_context

    package_name = uv_library_context["project_name"].replace("-", "_").lower()
    main_py_path = os.path.join(uv_library_project.project_path, f"src/{package_name}/main.py")
    assert not os.path.exists(main_py_path), "Library should not have main.py"


def test_uv_library_has_examples(uv_library_project: Result) -> None:
    """Test that UV library projects keep the example that 'make run' falls back to."""
    example_path = os.path.join(uv_library_project.project_path, "examples/main.py")
    assert os.path.exists(example_path), "Library should have examples/main.py"


def test_uv_application_has_no_examples(uv_application_project: Result) -> None:
    """Test that UV application projects drop examples/ in favour of the console script."""
    examples_dir = os.path.join(uv_application_project.project_path, "examples")
    assert not os.path.exists(examples_dir), "Application should not have an examples/ directory"


def test_uv_run_uses_uv(uv_default_project: Result) -> None:
    """Test that the UV template's run function invokes uv, not poetry."""
    run_sh_path = os.path.join(uv_default_project.project_path, "run.sh")
    with open(run_sh_path) as f:
        content = f.read()

    project_name = os.path.basename(uv_default_project.project_path)
    assert f'uv run {project_name} "$@"' in content, "UV template should run the console script via uv"


def test_uv_supacode_json_absent_by_default(uv_default_project: Result) -> None:
    """Test that the UV template also keeps supacode.json opt-in."""
    assert not os.path.exists(os.path.join(uv_default_project.project_path, "supacode.json"))


def test_uv_worktree_functions_present(uv_default_project: Result) -> None:
    """The worktree commands ship unconditionally; only supacode.json is gated by the flag."""
    run_sh_path = os.path.join(uv_default_project.project_path, "run.sh")
    with open(run_sh_path) as f:
        content = f.read()

    for name in ("worktree:hook", "worktree:setup", "worktree:archive", "worktree:delete"):
        assert f"function {name} " in content, f"missing '{name}' in run.sh"


def test_uv_project_structure(uv_default_project: Result) -> None:
    """Test that UV project has all required files."""
    from tests.project_structure import expected_files

    for path in expected_files:
        assert os.path.exists(
            os.path.join(uv_default_project.project_path, path)
        ), f"Missing file or directory: {path}"
