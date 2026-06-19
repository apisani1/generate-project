"""Tests for installing the bundled Claude assets (release-docs skill + command).

The set of files to install lives in a single auto-generated manifest
(claude_assets/asset_manifest.txt). These tests read that manifest rather than
hardcoding paths, and guard that it stays fresh and that the two template installer
scripts carry no duplicate hardcoded list.
"""

import importlib.util
import sys
from pathlib import Path

from generate_project.skills import (
    claude_assets_dir,
    generate_manifest_lines,
    install_claude_skills,
    read_manifest,
)

# Files we always expect to exist, asserted by name so the presence test is not a
# tautology against the manifest/walk. Adding assets does not require editing this.
REQUIRED_ANCHORS = {
    "skills/release-docs/SKILL.md",
    "commands/release-docs.md",
    "skills/generate-codex-assets/SKILL.md",
    "skills/generate-codex-assets/scripts/generate_codex_assets.py",
}

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "src" / "generate_project" / "templates"
CLAUDE_ASSETS_DIR = Path(__file__).resolve().parent.parent / "src" / "generate_project" / "claude_assets"
INSTALLER_PATHS = [
    TEMPLATES_DIR / "uv-template" / "{{cookiecutter.project_name}}" / "scripts" / "install_claude_skills.py",
    TEMPLATES_DIR / "poetry-template" / "{{cookiecutter.project_name}}" / "scripts" / "install_claude_skills.py",
]
CODEX_GENERATOR_PATH = CLAUDE_ASSETS_DIR / "skills" / "generate-codex-assets" / "scripts" / "generate_codex_assets.py"


def _load_installer(path: Path):
    """Import a template installer script by file path (no import-time side effects)."""
    spec = importlib.util.spec_from_file_location(path.parent.parent.name.replace("-", "_") + "_installer", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_codex_generator():
    """Import the Codex asset generator script by file path."""
    spec = importlib.util.spec_from_file_location("generate_codex_assets", CODEX_GENERATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    old_dont_write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = old_dont_write_bytecode
    return module


def test_manifest_is_up_to_date() -> None:
    """The committed manifest must match the asset tree (CI freshness guard)."""
    assert read_manifest() == generate_manifest_lines(), (
        "asset_manifest.txt is stale; run `make manifest` "
        "(or python -m generate_project.skills --write-manifest) and commit it"
    )


def test_bundled_assets_present() -> None:
    """The package must ship the always-expected anchor assets, listed in the manifest."""
    manifest = set(read_manifest())
    base = claude_assets_dir()
    assert REQUIRED_ANCHORS <= manifest, f"missing manifest entries: {REQUIRED_ANCHORS - manifest}"
    for rel in REQUIRED_ANCHORS:
        assert (base / rel).is_file(), f"missing bundled asset: {rel}"


def test_manifest_not_installed_into_claude(tmp_path: Path) -> None:
    """The manifest itself is metadata and must not be copied into a .claude dir."""
    dest = tmp_path / ".claude"
    install_claude_skills(dest)
    assert not (dest / "asset_manifest.txt").exists()


def test_install_copies_all_assets(tmp_path: Path) -> None:
    dest = tmp_path / ".claude"
    installed, skipped = install_claude_skills(dest)

    expected = set(read_manifest())
    assert skipped == []
    installed_rel = {str(p.relative_to(dest)) for p in installed}
    assert installed_rel == expected
    for rel in expected:
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
    assert len(skipped) == len(read_manifest())
    assert command.read_text() == "LOCAL EDIT"


def test_install_force_overwrites(tmp_path: Path) -> None:
    dest = tmp_path / ".claude"
    install_claude_skills(dest)
    command = dest / "commands/release-docs.md"
    command.write_text("LOCAL EDIT")

    installed, skipped = install_claude_skills(dest, force=True)

    assert skipped == []
    assert len(installed) == len(read_manifest())
    assert command.read_text() != "LOCAL EDIT"


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    dest = tmp_path / ".claude"
    installed, skipped = install_claude_skills(dest, dry_run=True)

    assert len(installed) == len(read_manifest())
    assert not dest.exists()


def test_installers_have_no_hardcoded_list() -> None:
    """Both template installers must read the manifest, not carry a duplicate file list."""
    for path in INSTALLER_PATHS:
        module = _load_installer(path)
        assert not hasattr(module, "ASSET_FILES"), f"{path} still hardcodes ASSET_FILES"


def test_installers_are_identical() -> None:
    """The two template installer copies must stay byte-identical."""
    contents = {path.read_bytes() for path in INSTALLER_PATHS}
    assert len(contents) == 1, "uv-template and poetry-template install_claude_skills.py have diverged"


def test_codex_generator_uses_manifest_for_skills_and_prompts(tmp_path: Path) -> None:
    """Codex generation is driven by manifest structure, not by known asset names."""
    assets = tmp_path / "claude_assets"
    skill = assets / "skills" / "example-skill"
    command = assets / "commands"
    skill.mkdir(parents=True)
    command.mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: example-skill\ndescription: Example\n---\n\nDo it.\n")
    (skill / "helper.txt").write_text("helper\n")
    (command / "example-command.md").write_text(
        '---\ndescription: Example command\nargument-hint: "[value]"\n---\n\nUse $ARGUMENTS.\n'
    )
    (assets / "asset_manifest.txt").write_text(
        "\n".join(
            [
                "# generated",
                "skills/example-skill/SKILL.md",
                "skills/example-skill/helper.txt",
                "commands/example-command.md",
                "",
            ]
        )
    )

    generator = _load_codex_generator()
    source, reports = generator.install_from_assets(
        assets,
        tmp_path / ".agents" / "skills",
        include_prompts=True,
        prompt_dest=tmp_path / ".codex" / "prompts",
    )

    assert "local assets" in source.description
    assert [report.kind for report in reports] == ["Codex skill", "Codex prompt"]
    assert (tmp_path / ".agents" / "skills" / "example-skill" / "SKILL.md").read_text().endswith("Do it.\n")
    assert (tmp_path / ".agents" / "skills" / "example-skill" / "helper.txt").read_text() == "helper\n"
    assert (tmp_path / ".codex" / "prompts" / "example-command.md").read_text().endswith("Use $ARGUMENTS.\n")


def test_codex_generator_skips_existing_without_force(tmp_path: Path) -> None:
    assets = tmp_path / "claude_assets"
    skill = assets / "skills" / "example-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("SOURCE\n")
    (assets / "asset_manifest.txt").write_text("skills/example-skill/SKILL.md\n")
    dest = tmp_path / ".agents" / "skills"

    generator = _load_codex_generator()
    generator.install_from_assets(assets, dest)
    installed_file = dest / "example-skill" / "SKILL.md"
    installed_file.write_text("LOCAL EDIT\n")
    _, reports = generator.install_from_assets(assets, dest)

    assert reports[0].installed == []
    assert reports[0].skipped == [installed_file]
    assert installed_file.read_text() == "LOCAL EDIT\n"
