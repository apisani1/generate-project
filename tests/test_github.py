"""Test GitHub integration features."""

import os

import pytest

import yaml
from pytest_cookies.plugin import Result
from tests.project_structure import github_workflow_files


def test_github_workflows(default_project: Result) -> None:
    """Test that GitHub workflows are valid YAML."""

    for workflow_file in github_workflow_files:
        # Use project_path to get the full path to the generated project
        workflow_path = os.path.join(default_project.project_path, workflow_file)
        assert os.path.exists(workflow_path)

        try:
            with open(workflow_path) as f:
                workflow = yaml.safe_load(f)

            # Check required sections
            assert "name" in workflow
            assert "jobs" in workflow

        except Exception as e:
            pytest.fail(f"Invalid YAML in {workflow_file}: {e}")


def test_github_variables_templating(default_project: Result) -> None:
    """Test that GitHub workflows use correct templating."""

    for workflow_file in github_workflow_files:
        workflow_path = os.path.join(default_project.project_path, workflow_file)
        with open(workflow_path) as f:
            content = f.read()

        # Check that no unprocessed cookiecutter variables remain
        assert "{{ cookiecutter." not in content, f"Unprocessed cookiecutter variable in {workflow_file}"

        # GitHub variables should remain as ${{ ... }}
        assert "${{" in content, f"GitHub variables missing in {workflow_file}"

        # Check that no Jinja2 tags remain
        assert "{%" not in content, f"Unprocessed Jinja2 tags in {workflow_file}"


def test_readthedocs_config(default_project: Result) -> None:
    """Test that ReadTheDocs config is valid."""
    rtd_config_path = os.path.join(default_project.project_path, ".readthedocs.yaml")
    assert os.path.exists(rtd_config_path)

    try:
        with open(rtd_config_path) as f:
            config = yaml.safe_load(f)

        # Check required keys
        assert "version" in config
        assert "build" in config
        assert "commands" in config["build"]
        assert "pip install poetry" in config["build"]["commands"]
    except Exception as e:
        pytest.fail(f"Invalid YAML in .readthedocs.yaml: {e}")
