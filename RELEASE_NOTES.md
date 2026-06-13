# generate-project 2.1.0

This release brings the Claude Code workflow into generate-project itself: the
`release-docs` skill and companion commands now ship with the package, and the release
tooling is reworked around pre-written drafts and a committed `RELEASE_NOTES.md`. All
changes are mirrored in both the UV and Poetry project templates.

## Highlights

- **Install the Claude assets anywhere.** `generate-project install-skills` installs the
  `release-docs` skill and `/release-docs` command globally into `~/.claude`; `generate
  --install-skills` installs them into a new project's `.claude/`; and an already-generated
  repo can run `python scripts/install_claude_skills.py` (which copies from the installed
  package or downloads from GitHub).
- **Draft your releases ahead of time.** `scripts/release.py create --release-docs` reads
  `commit.txt`, `tag.txt`, `changelog.md`, and `release_notes.md` from `.tmp_release_docs/`
  and uses each draft when it exists, is non-empty, and is newer than the previous tag;
  anything missing or stale falls back to generated content (prompted interactively, warned
  in CI). The `/release-docs` skill can produce all four from the diff since the last release.
- **Committed `RELEASE_NOTES.md`** — generated and committed each release. `release.yml` uses
  it as the GitHub Release body when it was part of the tagged commit; otherwise it extracts
  that version's `CHANGELOG.md` entry.

## Added
- `generate-project install-skills` (with `--dest`, `--force`, `--dry-run`) and the
  `generate --install-skills` flag.
- Bundled Claude assets under `src/generate_project/claude_assets/` — the `release-docs`
  skill plus the `/release-docs`, `/update-dev-env`, and `/migrate-poetry-to-uv` commands —
  as the single source of truth.
- A templated `scripts/install_claude_skills.py` in both templates for collaborators without
  generate-project.
- An auto-generated asset manifest (`make manifest`) as the single list of files to install.
- `--release-docs [DIR]` support in `scripts/release.py`, a committed `RELEASE_NOTES.md`, and a
  per-release PyPI badge cache-bust.

## Changed
- `make release-*` now use `--release-docs` instead of prompting for changes inline, and
  `scripts/release.py` was refactored into separate commit / tag / changelog / release-notes
  builders.
- `run.sh` `lint:diff` honors the mypy `exclude` regex, so `make pre-commit` matches
  `make check`; `make format` / `make pre-commit` also regenerate the manifest.
- `docs.yml` PR documentation-preview comment no longer fails the docs check on fork PRs;
  isort declares `generate_project` as `known_first_party`; VS Code invokes pylint via the
  package manager.

## Deprecated
- `scripts/release.py --changes` — use `.tmp_release_docs/` drafts instead.

## Fixed
- Explicit `None` return after the release-doc fallback prompt; Poetry template `run.sh`
  Python 3 PATH fix.

## Documentation
- Corrected the package-manager default (UV) across README and docs, documented the release
  workflow and drafts, added a Project Types section, and expanded the CLAUDE.md gotchas.
- Documented the `install-skills` command and the bundled `/release-docs`, `/update-dev-env`,
  and `/migrate-poetry-to-uv` commands (plus `generate --install-skills`) in the README and
  command reference.

## Upgrade notes
No breaking changes. If you script releases with `release.py --changes`, migrate to
`--release-docs` drafts — `--changes` still works but is deprecated.
