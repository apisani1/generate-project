"""The general --help lists each command once, consistently, within 80 columns."""

import re

import pytest

import generate_project.main as gp_main

COMMANDS = ("generate", "config", "install-skills")


@pytest.fixture
def general_help(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> str:
    monkeypatch.setenv("COLUMNS", "80")
    monkeypatch.setattr("sys.argv", ["generate-project", "--help"])
    with pytest.raises(SystemExit) as exc:
        gp_main.main()
    assert exc.value.code == 0
    return capsys.readouterr().out


def test_every_line_fits_in_80_columns(general_help: str) -> None:
    too_long = [line for line in general_help.splitlines() if len(line) >= 80]
    assert not too_long, too_long


def test_commands_are_listed_once_in_one_block(general_help: str) -> None:
    assert "positional arguments" not in general_help
    assert "{generate,config,install-skills}" not in general_help
    assert re.search(r"^commands:$", general_help, re.M)


@pytest.mark.parametrize("command", COMMANDS)
def test_each_command_is_described_on_its_own_line(general_help: str, command: str) -> None:
    """Every command, install-skills included, has its description on the same line as its name."""
    assert re.search(rf"^    {re.escape(command)}\s+\S", general_help, re.M), general_help


def test_quick_start_covers_every_command(general_help: str) -> None:
    quick_start = general_help.split("Quick start:")[1]
    for command in COMMANDS:
        assert f"generate-project {command}" in quick_start
