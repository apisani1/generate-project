"""Tests for the confirmation prompt shown before using a template from outside the package."""

import io
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
)

import pytest

import generate_project.main as gp_main
from generate_project.main import (
    confirm_custom_template,
    is_bundled_template,
)

BUNDLED = Path(gp_main.__file__).parent / "templates" / "uv-template"


@pytest.fixture
def custom_template(tmp_path: Path) -> Path:
    template = tmp_path / "my-template"
    (template / "hooks").mkdir(parents=True)
    (template / "hooks" / "post_gen_project.py").write_text("print('hi')\n")
    return template


@pytest.fixture
def calls(monkeypatch: pytest.MonkeyPatch) -> List[Dict[str, Any]]:
    recorded: List[Dict[str, Any]] = []
    monkeypatch.setattr(gp_main, "generate_project", lambda **kw: recorded.append(kw))
    return recorded


def _run(monkeypatch: pytest.MonkeyPatch, *argv: str) -> None:
    monkeypatch.setattr("sys.argv", ["generate-project", "generate", "proj", *argv])
    gp_main.main()


def _tty(monkeypatch: pytest.MonkeyPatch, answer: str) -> None:
    stdin = io.StringIO(answer + "\n")
    stdin.isatty = lambda: True  # type: ignore[method-assign]
    monkeypatch.setattr("sys.stdin", stdin)
    monkeypatch.setattr("builtins.input", lambda prompt="": answer)


def test_is_bundled_template(custom_template: Path) -> None:
    assert is_bundled_template(BUNDLED)
    assert is_bundled_template(BUNDLED / ".." / "poetry-template")
    assert not is_bundled_template(custom_template)
    assert not is_bundled_template(BUNDLED / ".." / ".." / "..")


def test_bundled_template_does_not_prompt(monkeypatch: pytest.MonkeyPatch, calls: List[Dict[str, Any]]) -> None:
    monkeypatch.setattr("builtins.input", lambda prompt="": pytest.fail("must not prompt"))
    _run(monkeypatch)
    assert len(calls) == 1


def test_custom_template_without_terminal_is_refused(
    monkeypatch: pytest.MonkeyPatch, calls: List[Dict[str, Any]], custom_template: Path
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    with pytest.raises(SystemExit) as exc:
        _run(monkeypatch, "--template", str(custom_template))
    assert exc.value.code == 1
    assert not calls


@pytest.mark.parametrize("answer", ["y", "Y", "yes"])
def test_custom_template_confirmed_interactively(
    monkeypatch: pytest.MonkeyPatch, calls: List[Dict[str, Any]], custom_template: Path, answer: str
) -> None:
    _tty(monkeypatch, answer)
    _run(monkeypatch, "--template", str(custom_template))
    assert len(calls) == 1


@pytest.mark.parametrize("answer", ["", "n", "no", "maybe"])
def test_custom_template_declined(
    monkeypatch: pytest.MonkeyPatch, calls: List[Dict[str, Any]], custom_template: Path, answer: str
) -> None:
    _tty(monkeypatch, answer)
    with pytest.raises(SystemExit) as exc:
        _run(monkeypatch, "--template", str(custom_template))
    assert exc.value.code == 1
    assert not calls


def test_yes_flag_skips_prompt_and_is_not_passed_to_cookiecutter(
    monkeypatch: pytest.MonkeyPatch, calls: List[Dict[str, Any]], custom_template: Path
) -> None:
    monkeypatch.setattr("builtins.input", lambda prompt="": pytest.fail("must not prompt"))
    _run(monkeypatch, "--template", str(custom_template), "--yes")
    assert len(calls) == 1
    assert "assume_yes" not in calls[0]
    assert calls[0]["template_path"] == custom_template


def test_warning_lists_hook_scripts(capsys: pytest.CaptureFixture[str], custom_template: Path) -> None:
    assert confirm_custom_template(custom_template, assume_yes=True)
    out = capsys.readouterr().out
    assert "post_gen_project.py" in out
    assert "arbitrary code" in out
