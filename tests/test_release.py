"""Exhaustive bump_version matrix tests."""

from itertools import product
from typing import Optional

import pytest
from packaging.version import Version

from scripts.release import PrereleaseType, ReleaseType, bump_version

BASE_VERSIONS = [
    "0.0.0",
    "0.0.1",
    "0.1.0",
    "0.1.2",
    "1.0.0",
    "1.2.0",
    "1.2.3",
    "2.0.0",
    "2.3.4",
]

SUFFIXES = [
    "",
    ".post1",
    ".dev1",
    "a1",
    "b1",
    "rc1",
    "a1.dev1",
    "b2.dev3",
    "rc3.dev4",
]

VERSIONS = [f"{base}{suffix}" for base, suffix in product(BASE_VERSIONS, SUFFIXES)]
RELEASE_TYPES = list(ReleaseType)
PRERELEASE_TYPES: list[Optional[PrereleaseType]] = [None, *list(PrereleaseType)]
CASES = list(product(VERSIONS, RELEASE_TYPES, PRERELEASE_TYPES))


def _uses_bump_from_pre_to_pre(
    current: Version,
    release_type: ReleaseType,
) -> bool:
    if current.pre is None:
        return False
    if release_type == ReleaseType.PRE:
        return True
    if release_type in {ReleaseType.MICRO, ReleaseType.MINOR, ReleaseType.MAJOR} and current.dev is not None:
        return True
    return False


def _is_prerelease_downgrade(current: Version, prerelease_type: Optional[PrereleaseType]) -> bool:
    if current.pre is None or prerelease_type is None:
        return False

    current_pre_type = current.pre[0]
    pre_hierarchy = {"a": 1, "b": 2, "rc": 3}
    return pre_hierarchy[prerelease_type.value] < pre_hierarchy[current_pre_type]


def _expects_value_error(
    current: Version,
    release_type: ReleaseType,
    prerelease_type: Optional[PrereleaseType],
) -> bool:
    if release_type == ReleaseType.DEV and prerelease_type is not None:
        return True
    if release_type == ReleaseType.POST and (
        prerelease_type is not None or current.pre is not None or current.dev is not None
    ):
        return True
    if _uses_bump_from_pre_to_pre(current, release_type) and _is_prerelease_downgrade(current, prerelease_type):
        return True
    return False


@pytest.mark.parametrize("current_text,release_type,prerelease_type", CASES)
def test_bump_version_is_monotonic(
    current_text: str,
    release_type: ReleaseType,
    prerelease_type: Optional[PrereleaseType],
) -> None:
    """Validate bump_version behavior across the full matrix."""
    current_version = Version(current_text)

    if _expects_value_error(current_version, release_type, prerelease_type):
        with pytest.raises(ValueError):
            bump_version(current_version, release_type, prerelease_type)
        return

    new_version = bump_version(current_version, release_type, prerelease_type)
    assert isinstance(new_version, Version)
    assert new_version > current_version


# ── Expected-value regression tests ──────────────────────────────────────────
# fmt: off
EXPECTED_VALUE_CASES = [
    # ── MICRO ────────────────────────────────────────────────────────────────
    # From stable
    ("1.2.3",          ReleaseType.MICRO, None,               "1.2.4"),
    ("1.2.3",          ReleaseType.MICRO, PrereleaseType.RC,  "1.2.4rc1"),
    ("1.2.3",          ReleaseType.MICRO, PrereleaseType.ALPHA, "1.2.4a1"),
    # From post
    ("1.2.3.post1",    ReleaseType.MICRO, None,               "1.2.4"),
    # From dev (dev-aware: micro stays)
    ("1.2.4.dev1",     ReleaseType.MICRO, None,               "1.2.4"),
    ("1.2.4.dev1",     ReleaseType.MICRO, PrereleaseType.RC,  "1.2.4rc1"),
    # Finalize pre-release to stable
    ("1.2.4rc1",       ReleaseType.MICRO, None,               "1.2.4"),
    ("1.2.4a3",        ReleaseType.MICRO, None,               "1.2.4"),
    ("1.2.4rc1.dev1",  ReleaseType.MICRO, None,               "1.2.4"),
    # From pre+dev with prerelease_type → bump_from_pre_to_pre
    ("1.2.4rc1.dev1",  ReleaseType.MICRO, PrereleaseType.RC,  "1.2.4rc2"),
    ("1.2.4a1.dev1",   ReleaseType.MICRO, PrereleaseType.RC,  "1.2.4rc1"),
    # From pre (no dev) with prerelease_type → next micro base
    ("1.2.4rc1",       ReleaseType.MICRO, PrereleaseType.RC,  "1.2.5rc1"),
    ("1.2.4rc1",       ReleaseType.MICRO, PrereleaseType.ALPHA, "1.2.5a1"),

    # ── MINOR ────────────────────────────────────────────────────────────────
    # From stable
    ("1.2.3",          ReleaseType.MINOR, None,               "1.3.0"),
    ("1.2.3",          ReleaseType.MINOR, PrereleaseType.RC,  "1.3.0rc1"),
    # From dev targeting minor (micro==0 → minor stays)
    ("1.3.0.dev1",     ReleaseType.MINOR, None,               "1.3.0"),
    ("1.3.0.dev1",     ReleaseType.MINOR, PrereleaseType.RC,  "1.3.0rc1"),
    # From dev targeting micro (micro!=0 → minor increments)
    ("1.2.4.dev1",     ReleaseType.MINOR, None,               "1.3.0"),
    # Finalize pre-release to stable
    ("1.3.0rc1",       ReleaseType.MINOR, None,               "1.3.0"),
    ("1.2.4rc1",       ReleaseType.MINOR, None,               "1.2.4"),
    # From pre+dev → bump_from_pre_to_pre
    ("1.3.0rc1.dev1",  ReleaseType.MINOR, PrereleaseType.RC,  "1.3.0rc2"),
    # From pre (no dev) → next minor base
    ("1.3.0rc1",       ReleaseType.MINOR, PrereleaseType.RC,  "1.4.0rc1"),

    # ── MAJOR ────────────────────────────────────────────────────────────────
    # From stable
    ("1.2.3",          ReleaseType.MAJOR, None,               "2.0.0"),
    ("1.2.3",          ReleaseType.MAJOR, PrereleaseType.RC,  "2.0.0rc1"),
    # From dev targeting major (minor==0, micro==0 → major stays)
    ("2.0.0.dev1",     ReleaseType.MAJOR, None,               "2.0.0"),
    ("2.0.0.dev1",     ReleaseType.MAJOR, PrereleaseType.RC,  "2.0.0rc1"),
    # From dev targeting micro (minor!=0 → major increments)
    ("1.2.4.dev1",     ReleaseType.MAJOR, None,               "2.0.0"),
    # From dev targeting minor (minor!=0 → major increments)
    ("1.3.0.dev1",     ReleaseType.MAJOR, None,               "2.0.0"),
    # Finalize pre-release to stable
    ("2.0.0rc1",       ReleaseType.MAJOR, None,               "2.0.0"),
    # From pre+dev → bump_from_pre_to_pre
    ("2.0.0rc1.dev1",  ReleaseType.MAJOR, PrereleaseType.RC,  "2.0.0rc2"),
    # From pre (no dev) → next major base
    ("2.0.0rc1",       ReleaseType.MAJOR, PrereleaseType.RC,  "3.0.0rc1"),

    # ── PRE ──────────────────────────────────────────────────────────────────
    # From stable (micro+1)
    ("1.2.3",          ReleaseType.PRE,   PrereleaseType.RC,  "1.2.4rc1"),
    ("1.2.3",          ReleaseType.PRE,   PrereleaseType.ALPHA, "1.2.4a1"),
    ("1.2.3",          ReleaseType.PRE,   None,               "1.2.4rc1"),
    # From dev (dev-aware: micro stays)
    ("1.2.4.dev1",     ReleaseType.PRE,   PrereleaseType.RC,  "1.2.4rc1"),
    # Same pre type → increment
    ("1.2.4rc1",       ReleaseType.PRE,   PrereleaseType.RC,  "1.2.4rc2"),
    ("1.2.4rc1",       ReleaseType.PRE,   None,               "1.2.4rc2"),
    ("1.2.4a1",        ReleaseType.PRE,   PrereleaseType.ALPHA, "1.2.4a2"),
    # Higher pre type → start new sequence
    ("1.2.4a1",        ReleaseType.PRE,   PrereleaseType.RC,  "1.2.4rc1"),
    ("1.2.4a1",        ReleaseType.PRE,   PrereleaseType.BETA, "1.2.4b1"),
    ("1.2.4b1",        ReleaseType.PRE,   PrereleaseType.RC,  "1.2.4rc1"),
    # pre+dev → strips dev, bumps pre
    ("1.2.4rc1.dev1",  ReleaseType.PRE,   PrereleaseType.RC,  "1.2.4rc2"),
    ("1.2.4rc1.dev1",  ReleaseType.PRE,   None,               "1.2.4rc2"),

    # ── DEV ──────────────────────────────────────────────────────────────────
    # From stable → next micro dev
    ("1.2.3",          ReleaseType.DEV,   None,               "1.2.4.dev1"),
    # From post → next micro dev
    ("1.2.3.post1",    ReleaseType.DEV,   None,               "1.2.4.dev1"),
    # From dev → increment dev number
    ("1.2.4.dev1",     ReleaseType.DEV,   None,               "1.2.4.dev2"),
    ("1.2.4.dev5",     ReleaseType.DEV,   None,               "1.2.4.dev6"),
    # From pre → dev of next pre number
    ("1.2.4rc1",       ReleaseType.DEV,   None,               "1.2.4rc2.dev1"),
    ("1.2.4a2",        ReleaseType.DEV,   None,               "1.2.4a3.dev1"),
    # From pre+dev → increment dev number (preserves pre segment)
    ("1.2.4rc1.dev1",  ReleaseType.DEV,   None,               "1.2.4rc1.dev2"),
    ("1.2.4a1.dev3",   ReleaseType.DEV,   None,               "1.2.4a1.dev4"),

    # ── POST ─────────────────────────────────────────────────────────────────
    ("1.2.3",          ReleaseType.POST,  None,               "1.2.3.post1"),
    ("1.2.3.post1",    ReleaseType.POST,  None,               "1.2.3.post2"),
    ("1.2.3.post5",    ReleaseType.POST,  None,               "1.2.3.post6"),

    # ── Edge: 0.0.0 ─────────────────────────────────────────────────────────
    ("0.0.0",          ReleaseType.MICRO, None,               "0.0.1"),
    ("0.0.0",          ReleaseType.MINOR, None,               "0.1.0"),
    ("0.0.0",          ReleaseType.MAJOR, None,               "1.0.0"),
    ("0.0.0",          ReleaseType.DEV,   None,               "0.0.1.dev1"),
    ("0.0.0.dev1",     ReleaseType.MICRO, None,               "0.0.0"),
    ("0.0.0.dev1",     ReleaseType.MINOR, None,               "0.0.0"),
    ("0.0.0.dev1",     ReleaseType.MAJOR, None,               "0.0.0"),
]
# fmt: on


@pytest.mark.parametrize("current_text,release_type,prerelease_type,expected", EXPECTED_VALUE_CASES)
def test_bump_version_expected_values(
    current_text: str,
    release_type: ReleaseType,
    prerelease_type: Optional[PrereleaseType],
    expected: str,
) -> None:
    """Verify exact output for key bump scenarios."""
    result = bump_version(Version(current_text), release_type, prerelease_type)
    assert result == Version(expected), f"{current_text} + {release_type.value}({prerelease_type}) → {result}, expected {expected}"
