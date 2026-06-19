#!/usr/bin/env python3
"""Generate Codex assets from generate-project's manifest-listed Claude assets."""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
)

REPO = "apisani1/generate-project"
ASSETS_SUBPATH = "src/generate_project/claude_assets"
MANIFEST_NAME = "asset_manifest.txt"
DEFAULT_SKILL_DEST = Path(".agents") / "skills"
DEFAULT_PROMPT_DEST = Path.home() / ".codex" / "prompts"


@dataclass
class SourceBundle:
    """Resolved asset source and manifest-listed payloads."""

    description: str
    files: Dict[str, bytes]


@dataclass
class InstallReport:
    """Files installed and skipped for one destination kind."""

    kind: str
    installed: List[Path]
    skipped: List[Path]


def parse_manifest(text: str) -> List[str]:
    """Parse manifest text into relative POSIX paths."""
    return [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]


def _safe_manifest_paths(paths: Iterable[str]) -> List[str]:
    """Reject manifest paths that could escape the source or destination root."""
    safe: List[str] = []
    for rel in paths:
        path = Path(rel)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Unsafe manifest path: " + rel)
        safe.append(rel)
    return safe


def _read_local_bundle(assets_dir: Path) -> SourceBundle:
    """Read manifest-listed files from a local assets directory."""
    manifest = assets_dir / MANIFEST_NAME
    rels = _safe_manifest_paths(parse_manifest(manifest.read_text()))
    files: Dict[str, bytes] = {}
    for rel in rels:
        src = assets_dir / rel
        if not src.is_file():
            raise FileNotFoundError("Manifest entry is missing: " + str(src))
        files[rel] = src.read_bytes()
    return SourceBundle("local assets (" + str(assets_dir) + ")", files)


def _candidate_checkout_dirs(start: Path) -> Iterable[Path]:
    """Yield possible checkout asset directories from ``start`` upward."""
    for parent in [start, *start.parents]:
        yield parent / ASSETS_SUBPATH


def _find_checkout_assets(script_dir: Path) -> Optional[Path]:
    """Find ``src/generate_project/claude_assets`` in cwd or near this script."""
    starts = [Path.cwd(), script_dir]
    seen = set()
    for start in starts:
        for candidate in _candidate_checkout_dirs(start.resolve()):
            if candidate in seen:
                continue
            seen.add(candidate)
            if (candidate / MANIFEST_NAME).is_file():
                return candidate
    return None


def _find_package_assets() -> Optional[Path]:
    """Find assets bundled with an installed ``generate_project`` package."""
    try:
        import generate_project  # type: ignore
    except ImportError:
        return None
    candidate = Path(generate_project.__file__).parent / "claude_assets"
    return candidate if (candidate / MANIFEST_NAME).is_file() else None


def _download(url: str) -> bytes:
    """Download a URL or raise a RuntimeError with context."""
    try:
        with urllib.request.urlopen(url) as response:  # noqa: S310
            return response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError("Failed to download " + url + ": " + str(exc)) from exc


def _confirm_download(ref: str, assume_yes: bool) -> bool:
    """Ask before using GitHub unless ``--yes`` was passed."""
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        print(
            "No local generate-project assets were found and stdin is not interactive; "
            "re-run with --yes to allow downloading from GitHub.",
            file=sys.stderr,
        )
        return False
    answer = input("Download generate-project assets from github.com/" + REPO + "@" + ref + "? [y/N] ")
    return answer.strip().lower() in ("y", "yes")


def _read_github_bundle(ref: str, assume_yes: bool) -> Optional[SourceBundle]:
    """Download manifest-listed files from GitHub."""
    if not _confirm_download(ref, assume_yes):
        return None
    base_url = "https://raw.githubusercontent.com/" + REPO + "/" + ref + "/" + ASSETS_SUBPATH + "/"
    rels = _safe_manifest_paths(parse_manifest(_download(base_url + MANIFEST_NAME).decode("utf-8")))
    files = {rel: _download(base_url + rel) for rel in rels}
    return SourceBundle("github.com/" + REPO + "@" + ref, files)


def resolve_source(
    *,
    assets_dir: Optional[Path] = None,
    ref: str = "main",
    assume_yes: bool = False,
    script_dir: Optional[Path] = None,
) -> SourceBundle:
    """Resolve assets from explicit dir, checkout, installed package, or GitHub."""
    if assets_dir is not None:
        return _read_local_bundle(assets_dir.expanduser())

    script_dir = script_dir or Path(__file__).resolve().parent
    checkout_assets = _find_checkout_assets(script_dir)
    if checkout_assets is not None:
        return _read_local_bundle(checkout_assets)

    package_assets = _find_package_assets()
    if package_assets is not None:
        return _read_local_bundle(package_assets)

    github_bundle = _read_github_bundle(ref, assume_yes)
    if github_bundle is None:
        raise RuntimeError("Aborted: no asset source available.")
    return github_bundle


def _write_file(target: Path, data: bytes, *, force: bool, dry_run: bool) -> Tuple[bool, Path]:
    """Write one file, returning ``(installed, target)``."""
    if target.exists() and not force:
        return False, target
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return True, target


def install_codex_skills(
    files: Dict[str, bytes],
    skill_dest: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
) -> InstallReport:
    """Install manifest-listed skill trees under a Codex skills destination."""
    installed: List[Path] = []
    skipped: List[Path] = []
    for rel, data in sorted(files.items()):
        parts = Path(rel).parts
        if len(parts) < 3 or parts[0] != "skills":
            continue
        skill_name = parts[1]
        inner = Path(*parts[2:])
        target = skill_dest.expanduser() / skill_name / inner
        did_install, path = _write_file(target, data, force=force, dry_run=dry_run)
        if did_install:
            installed.append(path)
        else:
            skipped.append(path)
    return InstallReport("Codex skill", installed, skipped)


def install_codex_prompts(
    files: Dict[str, bytes],
    prompt_dest: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
) -> InstallReport:
    """Install manifest-listed command markdown files as Codex prompt wrappers."""
    installed: List[Path] = []
    skipped: List[Path] = []
    for rel, data in sorted(files.items()):
        path = Path(rel)
        if len(path.parts) != 2 or path.parts[0] != "commands" or path.suffix != ".md":
            continue
        target = prompt_dest.expanduser() / path.name
        did_install, out_path = _write_file(target, data, force=force, dry_run=dry_run)
        if did_install:
            installed.append(out_path)
        else:
            skipped.append(out_path)
    return InstallReport("Codex prompt", installed, skipped)


def install_from_assets(
    assets_dir: Path,
    skill_dest: Path,
    *,
    include_prompts: bool = False,
    prompt_dest: Path = DEFAULT_PROMPT_DEST,
    force: bool = False,
    dry_run: bool = False,
) -> Tuple[SourceBundle, List[InstallReport]]:
    """Install Codex assets from a local assets directory; useful for tests."""
    bundle = _read_local_bundle(assets_dir)
    reports = [
        install_codex_skills(bundle.files, skill_dest, force=force, dry_run=dry_run),
    ]
    if include_prompts:
        reports.append(install_codex_prompts(bundle.files, prompt_dest, force=force, dry_run=dry_run))
    return bundle, reports


def _print_report(source: SourceBundle, reports: List[InstallReport], dry_run: bool) -> None:
    """Print a compact install summary."""
    verb = "Would install" if dry_run else "Installed"
    print("Source: " + source.description)
    for report in reports:
        print(verb + " " + str(len(report.installed)) + " " + report.kind + " file(s):")
        for path in report.installed:
            print("  + " + str(path))
        if report.skipped:
            print("Skipped " + str(len(report.skipped)) + " existing " + report.kind + " file(s):")
            for path in report.skipped:
                print("  = " + str(path))


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Codex skills and optional prompt wrappers from generate-project assets."
    )
    parser.add_argument("--assets-dir", type=Path, help="Use a specific claude_assets directory")
    parser.add_argument("--skill-dest", type=Path, default=DEFAULT_SKILL_DEST, help="Codex skill destination")
    parser.add_argument("--prompts", action="store_true", help="Also install command files as Codex prompts")
    parser.add_argument("--prompt-dest", type=Path, default=DEFAULT_PROMPT_DEST, help="Codex prompt destination")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be installed without writing")
    parser.add_argument("--yes", action="store_true", help="Allow GitHub download without prompting")
    parser.add_argument("--ref", default="main", help="Git ref to download from when no local source exists")
    args = parser.parse_args(argv)

    try:
        source = resolve_source(assets_dir=args.assets_dir, ref=args.ref, assume_yes=args.yes)
        reports = [
            install_codex_skills(source.files, args.skill_dest, force=args.force, dry_run=args.dry_run),
        ]
        if args.prompts:
            reports.append(
                install_codex_prompts(source.files, args.prompt_dest, force=args.force, dry_run=args.dry_run)
            )
        _print_report(source, reports, args.dry_run)
        if not args.dry_run:
            print("Restart Codex or start a new session if newly installed skills/prompts do not appear.")
        return 0
    except Exception as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
