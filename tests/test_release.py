"""Exhaustive bump_version matrix tests."""

from datetime import datetime
from itertools import product
from typing import Optional

import pytest
from packaging.version import Version

from scripts.release import PrereleaseType, ReleaseType, RollbackState, bump_version

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


@pytest.mark.manual
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
            bump_version(current_version, release_type, prerelease_type, interactive=False)
        return

    new_version = bump_version(current_version, release_type, prerelease_type, interactive=False)
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


@pytest.mark.manual
@pytest.mark.parametrize("current_text,release_type,prerelease_type,expected", EXPECTED_VALUE_CASES)
def test_bump_version_expected_values(
    current_text: str,
    release_type: ReleaseType,
    prerelease_type: Optional[PrereleaseType],
    expected: str,
) -> None:
    """Verify exact output for key bump scenarios."""
    result = bump_version(Version(current_text), release_type, prerelease_type, interactive=False)
    assert result == Version(expected), f"{current_text} + {release_type.value}({prerelease_type}) → {result}, expected {expected}"


# ── RollbackState unit tests ─────────────────────────────────────────────────


class TestRollbackState:
    """Tests for the RollbackState class."""

    def _make_state(self, tmp_path):
        """Create a RollbackState with PICKLE_FILE pointing to tmp_path."""
        state = RollbackState(datetime.now().astimezone(), Version("1.2.3"))
        state.PICKLE_FILE = str(tmp_path / "test_state.pkl")
        return state

    def test_init(self):
        dt = datetime.now().astimezone()
        version = Version("1.2.3")
        state = RollbackState(dt, version)
        assert state.start_dt == dt
        assert state.current_version == version
        assert state.files_backup == []

    def test_add_to_backup(self):
        state = RollbackState(datetime.now().astimezone(), Version("1.0.0"))
        state.add_to_backup([("a.txt", "content_a")])
        assert state.files_backup == [("a.txt", "content_a")]
        state.add_to_backup([("b.txt", "content_b"), ("c.txt", "content_c")])
        assert state.files_backup == [
            ("a.txt", "content_a"),
            ("b.txt", "content_b"),
            ("c.txt", "content_c"),
        ]

    def test_save_and_load(self, tmp_path, monkeypatch):
        state = self._make_state(tmp_path)
        state.add_to_backup([("file.txt", "original")])
        pickle_path = state.PICKLE_FILE
        state.save()

        monkeypatch.setattr(RollbackState, "PICKLE_FILE", pickle_path)
        loaded = RollbackState.load()
        assert loaded.current_version == state.current_version
        assert loaded.start_dt == state.start_dt
        assert loaded.files_backup == [("file.txt", "original")]

    def test_load_file_not_found(self, tmp_path, monkeypatch):
        monkeypatch.setattr(RollbackState, "PICKLE_FILE", str(tmp_path / "missing.pkl"))
        with pytest.raises(FileNotFoundError):
            RollbackState.load()

    def test_restore_files(self, tmp_path):
        file_a = tmp_path / "a.txt"
        file_b = tmp_path / "b.txt"
        file_a.write_text("modified_a")
        file_b.write_text("modified_b")

        state = RollbackState(datetime.now().astimezone(), Version("1.0.0"))
        state.files_backup = [(str(file_a), "original_a"), (str(file_b), "original_b")]
        state.restore_files()

        assert file_a.read_text() == "original_a"
        assert file_b.read_text() == "original_b"

    def test_restore_files_skips_missing(self, tmp_path):
        state = RollbackState(datetime.now().astimezone(), Version("1.0.0"))
        state.files_backup = [(str(tmp_path / "nonexistent.txt"), "content")]
        state.restore_files()  # should not raise

    def test_cleanup_removes_pickle(self, tmp_path):
        state = self._make_state(tmp_path)
        state.save()
        assert (tmp_path / "test_state.pkl").exists()
        state.cleanup()
        assert not (tmp_path / "test_state.pkl").exists()

    def test_cleanup_no_file(self, tmp_path):
        state = self._make_state(tmp_path)
        state.cleanup()  # should not raise
