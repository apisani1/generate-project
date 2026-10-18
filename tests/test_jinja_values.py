"""Option and config.yaml values are rendered as Jinja by cookiecutter, so Jinja syntax must be rejected."""

from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
)

import pytest
import yaml

import generate_project.main as gp_main
from generate_project.main import (
    check_no_jinja,
    contains_jinja,
    validate_user_config,
)

TEMPLATES = Path(gp_main.__file__).parent / "templates"
PAYLOADS = [
    "{{ 7*7 }}",
    "{{cycler.__init__.__globals__.os.popen('id').read()}}",
    "{% for x in range(3) %}x{% endfor %}",
    "{# comment #}",
    "prefix {{ cookiecutter.project_name }} suffix",
]


@pytest.mark.parametrize("value", PAYLOADS)
def test_contains_jinja_detects_payloads(value: str) -> None:
    assert contains_jinja(value)
    with pytest.raises(ValueError):
        check_no_jinja("author_name", value)


@pytest.mark.parametrize("value", ["Jane Doe", "A {single} brace", "100% sure", "a#b", "a }} b", ""])
def test_ordinary_values_are_accepted(value: str) -> None:
    assert check_no_jinja("author_name", value) == value


def test_trusted_default_is_allowed_but_only_exactly() -> None:
    default = "{{ cookiecutter.project_name.lower() }}"
    assert check_no_jinja("package_name", default, trusted=default) == default
    with pytest.raises(ValueError):
        check_no_jinja("package_name", default + "{{ evil }}", trusted=default)


def test_shipped_defaults_and_config_yaml_pass_validation() -> None:
    import json

    defaults = json.loads((TEMPLATES / "uv-template" / "cookiecutter.json").read_text())
    user = yaml.safe_load((TEMPLATES / "config.yaml").read_text()).get("default_context", {})
    validate_user_config(user, defaults, TEMPLATES / "config.yaml")  # must not exit


def test_hostile_config_yaml_value_is_rejected(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        validate_user_config({"description": "{{ 7*7 }}"}, {}, Path("config.yaml"))
    assert exc.value.code == 1
    assert "description" in capsys.readouterr().out


def test_non_string_config_values_are_skipped() -> None:
    validate_user_config({"version": 1.0, "flag": True}, {}, Path("config.yaml"))


@pytest.fixture
def calls(monkeypatch: pytest.MonkeyPatch) -> List[Dict[str, Any]]:
    recorded: List[Dict[str, Any]] = []
    monkeypatch.setattr(gp_main, "generate_project", lambda **kw: recorded.append(kw))
    return recorded


def _run(monkeypatch: pytest.MonkeyPatch, *argv: str) -> None:
    monkeypatch.setattr("sys.argv", ["generate-project", *argv])
    gp_main.main()


@pytest.mark.parametrize("value", PAYLOADS)
def test_cli_option_with_jinja_is_rejected(
    monkeypatch: pytest.MonkeyPatch, calls: List[Dict[str, Any]], capsys: pytest.CaptureFixture[str], value: str
) -> None:
    with pytest.raises(SystemExit) as exc:
        _run(monkeypatch, "generate", "proj", "--description", value)
    assert exc.value.code == 2
    assert "template syntax" in capsys.readouterr().err
    assert not calls


@pytest.mark.parametrize("value", PAYLOADS)
def test_cli_project_name_with_jinja_is_rejected(
    monkeypatch: pytest.MonkeyPatch, calls: List[Dict[str, Any]], value: str
) -> None:
    with pytest.raises(SystemExit) as exc:
        _run(monkeypatch, "generate", value)
    assert exc.value.code == 2
    assert not calls


def test_config_command_rejects_jinja(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(gp_main, "update_config_file", lambda *a, **k: pytest.fail("must not save"))
    with pytest.raises(SystemExit) as exc:
        _run(monkeypatch, "config", "--author_name", "{{ 7*7 }}")
    assert exc.value.code == 2


def test_normal_generate_still_works_with_defaults(
    monkeypatch: pytest.MonkeyPatch, calls: List[Dict[str, Any]]
) -> None:
    """The shipped package_name default contains Jinja on purpose and must still be accepted."""
    _run(monkeypatch, "generate", "proj", "--author_name", "Jane Doe")
    assert len(calls) == 1
    assert calls[0]["author_name"] == "Jane Doe"
    assert "{{" in calls[0]["package_name"]


def test_generating_into_dir_with_jinja_name_is_rejected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    hostile = tmp_path / "{{ 7*7 }}"
    hostile.mkdir()
    monkeypatch.chdir(hostile)
    monkeypatch.setattr(gp_main, "expand_template", lambda *a, **k: pytest.fail("must not render"))
    with pytest.raises(SystemExit) as exc:
        gp_main.generate_project(
            project_name=".", template_path=gp_main.Path(TEMPLATES / "uv-template"), env_file=hostile
        )
    assert exc.value.code == 1
    assert "not a valid project name" in capsys.readouterr().out
