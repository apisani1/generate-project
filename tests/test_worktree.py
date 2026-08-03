"""Test the worktree lifecycle commands that Supacode's setup/archive/delete scripts call."""

import json
import os
import subprocess
from pathlib import Path

import pytest

from pytest_cookies.plugin import Result


REPO_ROOT = Path(__file__).resolve().parent.parent

SUPACODE_CONFIGS = (
    REPO_ROOT / "supacode.json",
    REPO_ROOT / "src/generate_project/templates/uv-template/{{cookiecutter.project_name}}/supacode.json",
    REPO_ROOT / "src/generate_project/templates/poetry-template/{{cookiecutter.project_name}}/supacode.json",
)


def run_sh(project_path: Path, *args: str, **env: str) -> subprocess.CompletedProcess:
    """Invoke ./run.sh in the generated project with a clean, unactivated environment."""
    child_env = dict(os.environ)
    # A worktree terminal may or may not have a venv active; the commands must not depend on one.
    child_env.pop("VIRTUAL_ENV", None)
    child_env.pop("_AUTO_MAKE_VENV_DIR", None)
    child_env.update(env)
    return subprocess.run(
        ["./run.sh", *args],
        cwd=project_path,
        env=child_env,
        capture_output=True,
        text=True,
        check=False,
    )


def git(project_path: Path, *args: str) -> None:
    """Run a git command in the generated project."""
    subprocess.run(["git", *args], cwd=project_path, check=True, capture_output=True)


@pytest.fixture
def committed_project(uv_supacode_project: Result) -> Path:
    """A generated project with an initial commit on the default branch."""
    path = Path(uv_supacode_project.project_path)
    git(path, "init", "-q")
    git(path, "-c", "user.email=t@t", "-c", "user.name=T", "commit", "--allow-empty", "-qm", "empty root")
    git(path, "add", "-A")
    git(path, "-c", "user.email=t@t", "-c", "user.name=T", "commit", "-qm", "Initial commit")
    return path


@pytest.fixture
def deletable_project(committed_project: Path) -> Path:
    """A project whose HEAD is reachable from another ref, so only the tree state can block."""
    git(committed_project, "branch", "-q", "feature")
    git(committed_project, "checkout", "-q", "feature")
    return committed_project


def test_supacode_json_identical_across_repo_and_templates() -> None:
    """This repo uses the same worktree config it ships, and all three copies must stay in sync."""
    for path in SUPACODE_CONFIGS:
        assert path.exists(), f"missing (is it caught by .gitignore?): {path}"

    reference = SUPACODE_CONFIGS[0].read_text()
    for path in SUPACODE_CONFIGS[1:]:
        assert path.read_text() == reference, f"{path} has drifted from {SUPACODE_CONFIGS[0]}"


def test_repo_supacode_json_is_tracked_by_git() -> None:
    """An unanchored .gitignore pattern would silently drop the templates' copies too."""
    for path in SUPACODE_CONFIGS:
        result = subprocess.run(
            ["git", "check-ignore", str(path)],
            cwd=REPO_ROOT,
            capture_output=True,
            check=False,
        )
        assert result.returncode != 0, f"{path} is git-ignored and would never be committed"


def test_supacode_scripts_match_run_sh_commands(uv_supacode_project: Result) -> None:
    """Every command named in supacode.json must exist as a run.sh function."""
    path = Path(uv_supacode_project.project_path)
    config = json.loads((path / "supacode.json").read_text())
    run_sh_source = (path / "run.sh").read_text()

    for key, command in config.items():
        assert command.startswith("./run.sh "), f"{key} should delegate to run.sh"
        function_name = command.split()[-1]
        assert f"function {function_name} " in run_sh_source, f"{key} calls missing '{function_name}'"


def test_delete_blocks_on_uncommitted_changes(deletable_project: Path) -> None:
    """A dirty working tree must stop deletion - this is the most common way to lose work."""
    (deletable_project / "scratch.txt").write_text("unsaved work")

    result = run_sh(deletable_project, "worktree:delete")

    assert result.returncode != 0, "deletion must be blocked"
    assert "BLOCKED: uncommitted changes" in result.stdout
    assert "scratch.txt" in result.stdout


def test_delete_blocks_on_orphaned_commits(committed_project: Path) -> None:
    """Commits reachable from no other ref must stop deletion; the branch dies with the worktree."""
    result = run_sh(committed_project, "worktree:delete")

    assert result.returncode != 0, "deletion must be blocked"
    assert "exist only on" in result.stdout


def test_delete_blocks_on_stash_entries(deletable_project: Path) -> None:
    """Stashes survive deletion but become orphaned and hard to trace back."""
    (deletable_project / "scratch.txt").write_text("work in progress")
    git(deletable_project, "add", "-A")
    git(deletable_project, "stash", "-q")

    result = run_sh(deletable_project, "worktree:delete")

    assert result.returncode != 0, "deletion must be blocked"
    assert "stash entry" in result.stdout


def test_delete_allows_a_clean_merged_worktree(deletable_project: Path) -> None:
    """Nothing to lose means deletion proceeds."""
    result = run_sh(deletable_project, "worktree:delete")

    assert result.returncode == 0, f"deletion should be allowed:\n{result.stdout}\n{result.stderr}"


def test_force_delete_overrides_every_guardrail(deletable_project: Path) -> None:
    """SUPACODE_FORCE_DELETE=1 is the escape hatch for deliberately discarding work."""
    (deletable_project / "scratch.txt").write_text("unsaved work")

    result = run_sh(deletable_project, "worktree:delete", SUPACODE_FORCE_DELETE="1")

    assert result.returncode == 0, f"force delete should proceed:\n{result.stdout}\n{result.stderr}"
    assert "skipping guardrails" in result.stdout


def test_archive_never_fails_without_a_remote(committed_project: Path) -> None:
    """A non-zero exit blocks archiving in Supacode, so a missing origin must not fail."""
    result = run_sh(committed_project, "worktree:archive")

    assert result.returncode == 0, f"archive must not fail:\n{result.stdout}\n{result.stderr}"
    assert not (committed_project / ".venv").exists(), "archive should reclaim the venv"


def test_hook_is_optional(committed_project: Path) -> None:
    """Absent scripts/worktree-<phase>.sh means success, not failure."""
    assert not (committed_project / "scripts" / "worktree-archive.sh").exists()

    result = run_sh(committed_project, "worktree:archive")

    assert result.returncode == 0


def test_hook_exit_code_propagates(committed_project: Path) -> None:
    """A per-repo hook decides the phase's outcome, so Supacode honours its verdict."""
    hook = committed_project / "scripts" / "worktree-archive.sh"
    hook.write_text("#!/usr/bin/env bash\nexit 3\n")
    hook.chmod(0o755)

    result = run_sh(committed_project, "worktree:archive")

    assert result.returncode == 3, f"hook exit code must propagate:\n{result.stdout}\n{result.stderr}"


def test_setup_discards_a_venv_copied_from_another_checkout(committed_project: Path) -> None:
    """New worktrees inherit the parent's .venv, whose absolute paths point elsewhere."""
    activate = committed_project / ".venv" / "bin" / "activate"
    activate.parent.mkdir(parents=True, exist_ok=True)
    activate.write_text("VIRTUAL_ENV='/somewhere/else/.venv'\n")

    result = run_sh(committed_project, "worktree:setup")

    assert result.returncode == 0, f"setup failed:\n{result.stdout}\n{result.stderr}"
    assert "Discarding .venv copied from /somewhere/else/.venv" in result.stdout
    assert "/somewhere/else" not in activate.read_text(), "the stale venv must be gone"


def test_setup_builds_a_usable_venv_without_shell_activation(committed_project: Path) -> None:
    """Users with no shell auto-activation hook must still get a working environment."""
    result = run_sh(committed_project, "worktree:setup")

    assert result.returncode == 0, f"setup failed:\n{result.stdout}\n{result.stderr}"
    activate = (committed_project / ".venv" / "bin" / "activate").read_text()
    assert str(committed_project.resolve()) in activate, "venv must point at this checkout"
    assert "not activated in this shell" in result.stdout, "the hint should tell them how to activate"
