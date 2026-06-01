#!/usr/bin/env python3
"""Find the previous release tag and print the git ranges to inspect.

This mirrors the version-tag convention used by generate-project's
``scripts/release.py``: a tag counts as a release when it matches

    ^v\\d+\\.\\d+\\.\\d+(?:[-.]?(?:a|alpha|b|beta|rc|dev|post)\\d*)?$

Matching tags are sorted with PEP 440 semantics (via ``packaging`` when it is
available, otherwise a best-effort numeric fallback) and the highest version is
reported as the previous release. When no tag matches, the full reachable
history is treated as unreleased and the equivalent "all history" commands are
printed instead.

Usage:
    python find_previous_release.py            # human-readable summary + commands
    python find_previous_release.py --tag-only  # print just the tag (empty if none)
"""

from __future__ import annotations

import re
import subprocess
import sys

# Same pattern as generate-project release.py uses to recognize release tags.
TAG_PATTERN = re.compile(r"^v\d+\.\d+\.\d+(?:[-.]?(?:a|alpha|b|beta|rc|dev|post)\d*)?$")

try:
    from packaging.version import Version

    _HAVE_PACKAGING = True
except ImportError:
    _HAVE_PACKAGING = False

# Fallback empty-tree hash for SHA-1 repos. Used only if `git hash-object` fails;
# normally we compute the empty tree below so SHA-256 repos work too.
EMPTY_TREE_SHA1 = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def _git(*args: str) -> str:
    result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return result.stdout


def _empty_tree() -> str:
    """Return this repo's empty-tree object hash.

    Diffing against the empty tree yields a diff of the entire reachable history.
    Computing it (rather than hardcoding the SHA-1 constant) keeps this correct for
    repositories using the SHA-256 object format, whose empty tree hash differs.
    """
    try:
        return _git("hash-object", "-t", "tree", "/dev/null").strip()
    except subprocess.CalledProcessError:
        return EMPTY_TREE_SHA1


def _sort_key(tag: str):
    """Sort key for a release tag, newest last. Strips the leading ``v``."""
    raw = tag[1:]
    if _HAVE_PACKAGING:
        return Version(raw)
    # Fallback when `packaging` isn't installed: split into components and coerce
    # numeric parts to ints so 2.0.10 sorts after 2.0.2. Good enough to pick the
    # maximum in common cases, but it can misrank pre-release/post/dev tags — see
    # the warning in find_previous_tag(). Install `packaging` for exact PEP 440 order.
    return [int(p) if p.isdigit() else p for p in re.split(r"[.\-]", raw)]


def find_previous_tag() -> str | None:
    try:
        tags = [t.strip() for t in _git("tag", "--list").splitlines() if t.strip()]
    except subprocess.CalledProcessError as exc:
        print(
            f"error: git failed (not a repository?): {exc.stderr.strip()}",
            file=sys.stderr,
        )
        raise SystemExit(2)

    matching = [t for t in tags if TAG_PATTERN.match(t)]
    if not matching:
        return None
    if not _HAVE_PACKAGING and len(matching) > 1:
        print(
            "warning: `packaging` is not installed; using approximate version ordering "
            "that may misrank pre-release/post/dev tags. Install it (e.g. "
            "`pip install packaging` or `uv add packaging`) for exact PEP 440 sorting.",
            file=sys.stderr,
        )
    try:
        matching.sort(key=_sort_key)
    except TypeError:
        # Heterogeneous fallback keys: fall back to lexical sort as a last resort.
        # This is the least accurate ordering, so flag that the pick may be wrong.
        print(
            "warning: could not order release tags by version (uncomparable keys); "
            "falling back to a lexical tag sort — the selected previous release may be "
            "wrong; verify it.",
            file=sys.stderr,
        )
        matching.sort()
    return matching[-1]


def main() -> int:
    tag_only = "--tag-only" in sys.argv[1:]
    previous = find_previous_tag()

    if tag_only:
        print(previous or "")
        return 0

    if previous:
        print(f"Previous release tag: {previous}\n")
        print("Inspect everything that changed since the previous release:")
        print(f"  git log {previous}..HEAD")
        print(f"  git diff {previous}..HEAD")
        print(f"  git diff --stat {previous}..HEAD")
    else:
        empty_tree = _empty_tree()
        print("No previous release tag found (no tag matches the release pattern).")
        print("Treating the full reachable history as unreleased.\n")
        print("Inspect the full history:")
        print("  git log")
        print(f"  git diff {empty_tree} HEAD")
        print(f"  git diff --stat {empty_tree} HEAD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
