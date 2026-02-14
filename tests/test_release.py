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
def test_bump_version_matrix(
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
