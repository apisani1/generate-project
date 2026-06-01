#!/usr/bin/env python3
"""Install the release-docs Claude skill and /release-docs command into this repo.

This project follows the generate-project release-docs convention: a Claude skill that
drafts release artifacts under .tmp_release_docs/ before you cut a release (consumed by
scripts/release.py via --release-docs). This script installs that skill + command into the
repository's own .claude/ directory so it is available when working in this repo.

Asset source, in order:
  1. An installed `generate_project` package (copies its bundled assets) — no network.
  2. Otherwise, download them from the generate-project GitHub repo (asks first).

Usage:
  python scripts/install_claude_skills.py             # into ./.claude (asks before any download)
  python scripts/install_claude_skills.py --force     # overwrite existing files
  python scripts/install_claude_skills.py --dry-run   # show what would happen
  python scripts/install_claude_skills.py --dest ~/.claude   # install globally instead
  python scripts/install_claude_skills.py --yes       # don't prompt before downloading
  python scripts/install_claude_skills.py --ref v2.1.0   # download from a specific git ref
"""

import argparse
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = "apisani1/generate-project"
ASSETS_SUBPATH = "src/generate_project/claude_assets"

# Files fetched when downloading from GitHub. The local-package path copies the whole
# asset tree dynamically, so this list only matters for the download fallback.
ASSET_FILES = [
    "skills/release-docs/SKILL.md",
    "skills/release-docs/agents/openai.yaml",
    "skills/release-docs/scripts/find_previous_release.py",
    "commands/release-docs.md",
]


def local_assets_dir():
    """Return the bundled claude_assets dir from an installed generate_project, or None."""
    try:
        import generate_project
    except ImportError:
        return None
    candidate = Path(generate_project.__file__).parent / "claude_assets"
    return candidate if candidate.is_dir() else None


def iter_local(assets_dir):
    """Yield (relative_path, source_file) for every bundled asset file."""
    for sub in ("skills", "commands"):
        base = assets_dir / sub
        if not base.is_dir():
            continue
        for src in sorted(base.rglob("*")):
            if src.is_file():
                yield str(src.relative_to(assets_dir)), src


def confirm_download(ref, assume_yes):
    """Ask before downloading from GitHub (unless --yes). Returns True to proceed."""
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        print(
            "generate_project is not installed and stdin is not interactive; "
            "re-run with --yes to allow downloading the skill files.",
            file=sys.stderr,
        )
        return False
    answer = input(f"Download release-docs skill files from github.com/{REPO}@{ref}? [y/N] ")
    return answer.strip().lower() in ("y", "yes")


def install(dest, force, dry_run, ref, assume_yes):
    dest = dest.expanduser()
    assets_dir = local_assets_dir()

    if assets_dir is not None:
        items = list(iter_local(assets_dir))
        payloads = {}
        source_desc = "installed generate_project (" + str(assets_dir) + ")"
    else:
        if not confirm_download(ref, assume_yes):
            print("Aborted: no asset source available.", file=sys.stderr)
            return 1
        base_url = "https://raw.githubusercontent.com/" + REPO + "/" + ref + "/" + ASSETS_SUBPATH + "/"
        payloads = {}
        for rel in ASSET_FILES:
            url = base_url + rel
            try:
                with urllib.request.urlopen(url) as resp:  # noqa: S310
                    payloads[rel] = resp.read()
            except urllib.error.URLError as exc:
                print("error: failed to download " + url + ": " + str(exc), file=sys.stderr)
                return 1
        items = [(rel, None) for rel in ASSET_FILES]
        source_desc = "github.com/" + REPO + "@" + ref

    installed = []
    skipped = []
    for rel, src in items:
        target = dest / rel
        if target.exists() and not force:
            skipped.append(target)
            continue
        installed.append(target)
        if dry_run:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if rel in payloads:
            target.write_bytes(payloads[rel])
        else:
            shutil.copy2(src, target)

    verb = "Would install" if dry_run else "Installed"
    print(verb + " " + str(len(installed)) + " file(s) from " + source_desc + " into " + str(dest))
    for path in installed:
        print("  + " + str(path))
    if skipped:
        print("Skipped " + str(len(skipped)) + " existing file(s); pass --force to overwrite:")
        for path in skipped:
            print("  = " + str(path))
    return 0


def main():
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="Install the release-docs Claude skill/command into this repository."
    )
    parser.add_argument(
        "--dest", type=Path, default=repo_root / ".claude", help="Target .claude directory (default: <repo>/.claude)"
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be installed without writing")
    parser.add_argument("--yes", action="store_true", help="Do not prompt before downloading from GitHub")
    parser.add_argument("--ref", default="main", help="Git ref to download from when generate_project is absent")
    args = parser.parse_args()
    return install(args.dest, args.force, args.dry_run, args.ref, args.yes)


if __name__ == "__main__":
    raise SystemExit(main())
