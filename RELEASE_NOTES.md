# generate-project 2.4.0

This release adds a uniform way to run generated projects (`make run`) and
first-class Supacode worktree lifecycle support (`--supacode`), alongside a
fix for a venv-activation bug affecting git worktrees and copied checkouts.

## Added

- **`make run` / `./run.sh run`.** Every generated project now has a uniform
  way to launch under development: the console script for applications, or
  `examples/main.py` for libraries (both templates now ship this example).
  A per-repo `scripts/run.sh`, if present and executable, takes priority —
  the template-owned dispatch logic is never touched for project-specific
  launch commands.

- **`--supacode` flag.** Generates a `supacode.json` that wires Supacode's
  worktree lifecycle hooks to three new `run.sh` commands (also available as
  `make worktree-*`):
  - `worktree:setup` — discards a `.venv` inherited from the parent
    checkout and installs dev dependencies
  - `worktree:archive` — prunes stale remote-tracking branches and removes
    the venv and build/test caches
  - `worktree:delete` — refuses to proceed if the tree is dirty, if commits
    exist only on the current branch, or if the branch has stashes
    (override with `SUPACODE_FORCE_DELETE=1`), then tears down like archive

  Each phase calls an optional `scripts/worktree-<phase>.sh` for anything
  project-specific (e.g. tearing down docker services, freeing ports).

## Fixed

- **venv activation across copied checkouts.** `run.sh`'s `venv` target
  could silently activate a *different* checkout's Python environment when
  `.venv` was copied along with the directory (worktree tooling does this),
  because `uv`/`virtualenv` hardcode the creating path into `bin/activate`
  and console-script shebangs. It now always operates on the script's own
  directory, strips stale `.venv/bin` PATH entries unconditionally, and
  detects and recreates a copied `.venv`.
- The worktree-delete orphaned-commit check now uses `git for-each-ref`
  instead of `git rev-list --exclude=<ref> --all --not`, which silently
  drops the `--exclude` when combined with `--not`.

## Changed

- **Poetry projects:** `run.sh` now sets `POETRY_VIRTUALENVS_IN_PROJECT=true`,
  so Poetry creates its venv inside the project instead of its global cache.
  Existing Poetry-based projects will get a fresh in-project `.venv` on their
  next `poetry install`.
- The `update-dev-env` skill now treats the `run` and `worktree:*`
  targets/functions as template-owned during syncs (customizations migrate
  into the escape-hatch scripts rather than being preserved in place), and
  can create a `supacode.json` on request without ever overwriting an
  existing one.
- Modernized VSCode settings: dropped deprecated `python.linting.*` keys and
  per-tool path overrides in favor of `importStrategy=fromEnvironment`.
- Removed the version query parameter from the PyPI badge URL.

## Upgrade notes

No breaking changes for typical usage. If you use the Poetry template and
have an out-of-project venv cache, your next install will create a fresh
in-project `.venv` — expect a one-time reinstall of dependencies.
