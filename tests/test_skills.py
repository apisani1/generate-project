"""Tests for installing the bundled Claude assets (release-docs skill + command)."""

from pathlib import Path

from generate_project.skills import (
    claude_assets_dir,
    install_claude_skills,
)

EXPECTED_RELATIVE = {
    "skills/release-docs/SKILL.md",
    "skills/release-docs/agents/openai.yaml",
    "skills/release-docs/scripts/find_previous_release.py",
    "commands/release-docs.md",
}


def test_bundled_assets_present() -> None:
    """The package must ship the four release-docs assets."""
    base = claude_assets_dir()
    for rel in EXPECTED_RELATIVE:
        assert (base / rel).is_file(), f"missing bundled asset: {rel}"


def test_install_copies_all_assets(tmp_path: Path) -> None:
    dest = tmp_path / ".claude"
    installed, skipped = install_claude_skills(dest)

    assert skipped == []
    installed_rel = {str(p.relative_to(dest)) for p in installed}
    assert installed_rel == EXPECTED_RELATIVE
    for rel in EXPECTED_RELATIVE:
        assert (dest / rel).is_file()
    # Content matches the bundled source.
    base = claude_assets_dir()
    assert (dest / "commands/release-docs.md").read_text() == (base / "commands/release-docs.md").read_text()


def test_install_skips_existing_without_force(tmp_path: Path) -> None:
    dest = tmp_path / ".claude"
    install_claude_skills(dest)

    # Mutate one file; a second run without force must not overwrite it.
    command = dest / "commands/release-docs.md"
    command.write_text("LOCAL EDIT")
    installed, skipped = install_claude_skills(dest)

    assert installed == []
    assert len(skipped) == len(EXPECTED_RELATIVE)
    assert command.read_text() == "LOCAL EDIT"


def test_install_force_overwrites(tmp_path: Path) -> None:
    dest = tmp_path / ".claude"
    install_claude_skills(dest)
    command = dest / "commands/release-docs.md"
    command.write_text("LOCAL EDIT")

    installed, skipped = install_claude_skills(dest, force=True)

    assert skipped == []
    assert len(installed) == len(EXPECTED_RELATIVE)
    assert command.read_text() != "LOCAL EDIT"


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    dest = tmp_path / ".claude"
    installed, skipped = install_claude_skills(dest, dry_run=True)

    assert len(installed) == len(EXPECTED_RELATIVE)
    assert not dest.exists()
