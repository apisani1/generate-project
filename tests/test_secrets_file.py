"""Tests for create_secrets_file: owner-only permissions from creation, and no overwriting."""

import os
import stat
from pathlib import Path

import pytest

from generate_project.main import (
    ENV_FILE_TEMPLATE,
    TOKEN_NAMES,
    create_secrets_file,
)

pytestmark = pytest.mark.skipif(os.name == "nt", reason="POSIX permission bits")


@pytest.fixture(autouse=True)
def _tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in TOKEN_NAMES:
        monkeypatch.setenv(name, f"value-of-{name}")


def test_created_with_owner_only_permissions_even_with_open_umask(tmp_path: Path) -> None:
    old = os.umask(0)
    try:
        create_secrets_file(tmp_path, ".env", TOKEN_NAMES, ENV_FILE_TEMPLATE)
    finally:
        os.umask(old)
    path = tmp_path / ".env"
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert "PYPI_TOKEN=value-of-PYPI_TOKEN" in path.read_text()


def test_file_is_never_created_with_wider_permissions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The mode is set at creation (os.open), not fixed up afterwards with chmod."""
    modes = []
    real_open = os.open

    def spy(path, flags, mode=0o777, **kw):  # type: ignore[no-untyped-def]
        modes.append(mode)
        return real_open(path, flags, mode, **kw)

    monkeypatch.setattr(os, "open", spy)
    create_secrets_file(tmp_path, ".pypirc", TOKEN_NAMES, ENV_FILE_TEMPLATE)
    assert modes == [0o600]


def test_existing_file_is_not_overwritten(tmp_path: Path) -> None:
    path = tmp_path / ".env"
    path.write_text("keep me")
    create_secrets_file(tmp_path, ".env", TOKEN_NAMES, ENV_FILE_TEMPLATE)
    assert path.read_text() == "keep me"


def test_symlink_is_not_followed(tmp_path: Path) -> None:
    target = tmp_path / "victim.txt"
    target.write_text("victim")
    (tmp_path / ".env").symlink_to(target)
    create_secrets_file(tmp_path, ".env", TOKEN_NAMES, ENV_FILE_TEMPLATE)
    assert target.read_text() == "victim"
