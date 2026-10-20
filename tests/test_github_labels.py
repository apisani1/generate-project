"""The Dependabot labels are created together with the GitHub repository."""

import subprocess
from pathlib import Path
from typing import (
    Any,
    List,
)

import pytest
import yaml

import generate_project.main as gp_main
from generate_project.main import (
    DEPENDABOT_LABELS,
    create_github_labels,
)

TEMPLATES = Path(gp_main.__file__).parent / "templates"


def _result(returncode: int = 0, stderr: str = "") -> "subprocess.CompletedProcess[str]":
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout="", stderr=stderr)


@pytest.fixture
def commands(monkeypatch: pytest.MonkeyPatch) -> List[List[str]]:
    """Record every command; all succeed."""
    recorded: List[List[str]] = []

    def fake_run(cmd: List[str], **kwargs: Any) -> "subprocess.CompletedProcess[str]":
        recorded.append(cmd)
        return _result()

    monkeypatch.setattr(gp_main, "run_command", fake_run)
    return recorded


@pytest.mark.parametrize("template", ["uv-template", "poetry-template"])
def test_labels_match_the_dependabot_config_in_the_templates(template: str) -> None:
    """If a template asks for other labels, they must be created too."""
    path = TEMPLATES / template / "{{cookiecutter.project_name}}" / ".github" / "dependabot.yml"
    wanted = {label for update in yaml.safe_load(path.read_text())["updates"] for label in update.get("labels", [])}
    assert wanted == set(DEPENDABOT_LABELS)


def test_creates_each_label_with_gh(commands: List[List[str]]) -> None:
    create_github_labels("me/proj")
    created = {cmd[3]: cmd for cmd in commands}
    assert set(created) == {"dependencies", "github_actions"}
    for name, (color, description) in DEPENDABOT_LABELS.items():
        assert created[name][:3] == ["gh", "label", "create"]
        assert created[name][4:] == ["--repo", "me/proj", "--color", color, "--description", description]


def test_existing_labels_are_left_alone(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    exists = 'label with name "x" already exists; use `--force` to update its color and description'
    monkeypatch.setattr(gp_main, "run_command", lambda cmd, **kw: _result(1, exists))
    create_github_labels("me/proj")  # must not raise or exit
    out = capsys.readouterr().out
    assert out.count("Label already exists") == 2
    assert "Could not create" not in out


def test_a_failure_is_a_warning_and_the_next_label_is_still_tried(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    calls: List[str] = []

    def fake_run(cmd: List[str], **kwargs: Any) -> "subprocess.CompletedProcess[str]":
        calls.append(cmd[3])
        return _result(1, "HTTP 403: Resource not accessible") if cmd[3] == "dependencies" else _result()

    monkeypatch.setattr(gp_main, "run_command", fake_run)
    create_github_labels("me/proj")  # must not raise or exit
    assert calls == ["dependencies", "github_actions"]
    out = capsys.readouterr().out
    assert "Could not create label dependencies" in out and "Created label: github_actions" in out


@pytest.mark.parametrize("repo_exists", [False, True])
def test_generating_with_github_creates_the_labels(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, commands: List[List[str]], repo_exists: bool
) -> None:
    """New repo or existing repo: the labels are created either way (idempotently)."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(gp_main, "expand_template", lambda template, target_dir, **kw: target_dir.mkdir())
    monkeypatch.setattr(gp_main, "check_github_cli", lambda: True)
    monkeypatch.setattr(gp_main, "get_github_username", lambda: "me")
    monkeypatch.setattr(gp_main, "check_github_repo_exists", lambda name, user: repo_exists)

    gp_main.generate_project(
        project_name="proj",
        template_path=TEMPLATES / "uv-template",
        env_file=tmp_path / ".env",
        install_deps=False,
        create_github=True,
    )

    label_cmds = [cmd for cmd in commands if cmd[:3] == ["gh", "label", "create"]]
    assert [cmd[3] for cmd in label_cmds] == list(DEPENDABOT_LABELS)
    assert all(cmd[4:6] == ["--repo", "me/proj"] for cmd in label_cmds)


def test_no_labels_without_github(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, commands: List[List[str]]) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(gp_main, "expand_template", lambda template, target_dir, **kw: target_dir.mkdir())
    gp_main.generate_project(
        project_name="proj", template_path=TEMPLATES / "uv-template", env_file=tmp_path / ".env", install_deps=False
    )
    assert not [cmd for cmd in commands if cmd[:2] == ["gh", "label"]]
