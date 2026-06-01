"""Install the Claude assets (skills + slash commands) bundled with this package.

The assets live under ``claude_assets/`` next to this module and are copied into a
``.claude`` directory — either the user's global ``~/.claude`` (via the
``generate-project install-skills`` command) or a specific project's ``.claude``
(via ``generate --install-skills``). The layout under ``claude_assets`` mirrors the
``.claude`` layout, so installing is a straight copy of ``skills/`` and ``commands/``.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import (
    Iterator,
    List,
    Optional,
    Tuple,
)

CLAUDE_ASSETS_DIRNAME = "claude_assets"
# Top-level asset folders mirrored verbatim into the destination .claude directory.
ASSET_SUBDIRS = ("skills", "commands")


def claude_assets_dir() -> Path:
    """Return the path to the Claude assets bundled with the installed package."""
    return Path(__file__).parent / CLAUDE_ASSETS_DIRNAME


def _iter_assets(assets_dir: Path) -> Iterator[Tuple[Path, Path]]:
    """Yield ``(relative_path, source_file)`` for every file to install."""
    for subdir in ASSET_SUBDIRS:
        base = assets_dir / subdir
        if not base.is_dir():
            continue
        for src in sorted(base.rglob("*")):
            if src.is_file():
                yield src.relative_to(assets_dir), src


def install_claude_skills(
    dest: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
    assets_dir: Optional[Path] = None,
) -> Tuple[List[Path], List[Path]]:
    """Copy the bundled ``skills/`` and ``commands/`` into ``dest`` (a ``.claude`` dir).

    Args:
        dest: The ``.claude`` directory to install into (created if needed).
        force: Overwrite files that already exist (otherwise they are skipped).
        dry_run: Compute what would be installed without writing anything.
        assets_dir: Source assets directory; defaults to the package's bundled assets.

    Returns:
        A ``(installed, skipped)`` tuple of destination paths.
    """
    assets_dir = assets_dir or claude_assets_dir()
    installed: List[Path] = []
    skipped: List[Path] = []
    for rel_path, src in _iter_assets(assets_dir):
        target = dest / rel_path
        if target.exists() and not force:
            skipped.append(target)
            continue
        installed.append(target)
        if dry_run:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
    return installed, skipped
