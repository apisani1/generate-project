# Changelog

## [2.3.0] - 2026-06-19

### Added
- New **`generate-codex-assets`** Codex skill that installs generate-project
  maintenance skills (and optionally prompt wrappers) into Codex from the same
  `asset_manifest.txt` used by the Claude installers. Resolves assets from a
  local checkout, an installed package, or GitHub (with user consent).
  Supports `--dry-run`, `--force`, `--yes`, `--ref`, and `--prompts` flags.
  Manifest-driven — no hardcoded skill names.

### Fixed
- Asset manifest generator (`skills.py`) now excludes hidden directories and
  `__pycache__` entries from the manifest to avoid shipping non-asset files.

### Changed
- All `make release-*` targets now support an `ARGS` variable that is forwarded
  to `run.sh` and on to `scripts/release.py`
  (e.g. `make release-minor ARGS="--no-push"`).

### Internal
- ReadTheDocs release step in `.github/workflows/release.yml` (root and both
  templates) overhauled: adds an explicit sync call before version activation,
  waits 20 s for sync to complete, broadens the HTTP success check to any 2xx
  response, triggers explicit builds for both the new tag and `latest`, and
  emits a conditional step-summary line reflecting actual RTD outcome.

## [2.2.0] - 2026-06-15

### Added
- The release flow now regenerates the bundled Claude asset manifest
  (`claude_assets/asset_manifest.txt`) and includes any change in the release
  commit, guaranteeing a released package never ships a stale manifest.

### Changed
- `scripts/release.py` now guards the `generate_project.skills` import with
  `try`/`except`, making manifest regeneration a no-op in generated projects
  (which lack the module) so the same `release.py` can be shared verbatim across
  the root repo and both templates.
- `run.sh`: manifest regeneration moved from the `format` target to `check` (it
  is still refreshed by pre-commit and the release flow).

### Security
- Poetry template documentation requirements: pin `urllib3>=1.26.19`,
  `zipp>=3.19.1`, `idna>=3.15`, and `pygments>=2.20.0` (via Snyk) to avoid known
  vulnerabilities in transitive documentation dependencies.

## [2.1.0] - 2026-06-13

### Added
- `generate-project install-skills` command to install the bundled Claude assets (the `release-docs` skill and `/release-docs` command) globally into `~/.claude`, with `--dest`, `--force`, and `--dry-run` options.
- `generate --install-skills` flag to install those assets into a new project's `.claude/` before the initial commit.
- Bundled Claude assets under `src/generate_project/claude_assets/` as the single source of truth: the `release-docs` skill (SKILL.md, the `find_previous_release.py` helper, agents) plus the `/release-docs`, `/update-dev-env`, and `/migrate-poetry-to-uv` commands.
- A templated `scripts/install_claude_skills.py` in both the UV and Poetry templates, so collaborators without generate-project can install the assets (copies from the installed package, or downloads from GitHub on confirmation).
- Auto-generated asset manifest (`claude_assets/asset_manifest.txt`) as the single list of files to install, read by every consumer; regenerate with `make manifest`.
- `--release-docs [DIR]` flag on `scripts/release.py create` (defaults to `.tmp_release_docs`). It reads pre-written drafts — `commit.txt`, `tag.txt`, `changelog.md`, `release_notes.md` — and uses each verbatim when it exists, is non-empty, and is newer than the previous release tag; otherwise it warns (or prompts, interactively) and falls back to generated content for that draft.
- `RELEASE_NOTES.md`, generated and committed each release and used as the GitHub Release body when it is part of the tagged commit.
- Per-release `?v=<version>` cache-bust on the README PyPI badge so the image refreshes on GitHub.

### Changed
- Refactored `scripts/release.py` into separate commit / tag / changelog / release-notes message builders; normalized changelog whitespace and the `### Changes` heading.
- `make release-*` / `run.sh release:*` targets now use `--release-docs` instead of prompting for changes inline.
- `release.yml`: the "Prepare release notes" step uses the committed `RELEASE_NOTES.md` only when it was part of the tagged commit, otherwise extracts that version's `CHANGELOG.md` entry.
- `run.sh` `lint:diff` now honors the `[tool.mypy] exclude` regex from `pyproject.toml`, so `make pre-commit` matches `make check` linting semantics.
- `make format` / `make pre-commit` regenerate the asset manifest.
- `docs.yml`: grant `contents: read` and mark the PR documentation-preview comment step `continue-on-error`, so fork PRs (which get a read-only token) never fail the docs check over a cosmetic comment.
- isort now declares `generate_project` as `known_first_party`; VS Code settings invoke pylint through the package manager; corrected the pylint flag in the root project and both templates.
- All of the above propagated to both the UV and Poetry cookiecutter templates.

### Deprecated
- The `scripts/release.py --changes` flag; use `--release-docs` drafts instead.

### Fixed
- Release tooling now returns `None` explicitly after the release-doc fallback prompt.
- Poetry template `run.sh` Python 3 PATH fix.

### Documentation
- Corrected the package-manager default across README and docs (UV is the default; Poetry via `--manager poetry`), documented the release workflow and release drafts, and added a Project Types section.
- Documented the `install-skills` command and the bundled `/release-docs`, `/update-dev-env`, and `/migrate-poetry-to-uv` commands, plus the `generate --install-skills` flag, in the README and command reference.
- Expanded the CLAUDE.md gotchas (template sync, release drafts, Claude assets, the asset manifest, and `RELEASE_NOTES.md`), and propagated the release-drafts and `RELEASE_NOTES.md` notes into both templates' `CLAUDE.md`.

### Internal
- Hardened the `version_variable` substitution regex in `scripts/release.py` and `scripts/update_versions.py` to stop at a closing `)`, so the version-stamped badge URL is rewritten correctly.
- Excluded `claude_assets/` from flake8, mypy, pylint, and coverage (shipped data, not package code).
- `.gitignore` now ignores `.tmp_release_docs/`.

## [2.0.0.post1] - 2026-03-09

# Release v2.0.0.post1 — Documentation & Template Improvements

## Overview

Post-release with no functional changes. Improves Claude Code context files (CLAUDE.md) across the repo and both cookiecutter templates, and adds a private notes folder scaffold to generated projects.

---

## Improvements

### Claude Code Context (CLAUDE.md)
- **Repo CLAUDE.md**: Added `CLI Usage` section with practical examples for all major flag combinations; added `Environment & Prerequisites` section documenting required tokens (`PYPI_TOKEN`, `TEST_PYPI_TOKEN`, `RTD_TOKEN`) and `gh auth login` requirement; added `Gotchas` section covering template sync, `--library` behavior, config precedence, and more.
- **Template CLAUDE.md** (UV & Poetry): Added `Code Style` section (Black 119 chars, isort, flake8/pylint/mypy); added `Project Structure` placeholder prompting developers to document their project; added `Gotchas` placeholder with tip about the `#` key shortcut; added `@./notes` reference.

### Generated Project Templates (UV & Poetry)
- Added `notes/` to `.gitignore` in both templates (local-only private notes).
- Added `notes/project-notes.md` scaffold with sections for Overview, Ideas, Architecture Decisions, Claude Code Context, and References.


## [2.0.0] - 2026-02-23

# Release v2.0.0 - Migration to UV package manager

## Overview

v2.0.0 completes the migration of `generate-project` itself from Poetry to UV, and makes **UV the default package manager** for generated projects. Poetry remains fully supported via `--manager poetry`.

This is a major release due to the change in default behavior: projects generated without a `--manager` flag now use UV instead of Poetry.

---

## Breaking Changes

- **UV is now the default package manager.** Running `generate-project my-project` generates a UV-based project. To generate a Poetry project, use `--manager poetry`.
- `poetry.lock` has been replaced by `uv.lock` in this repository.
- Development workflow commands now use `uv` instead of `poetry` (see updated `CLAUDE.md` and `run.sh`).

---

## New Features

- **UV default template**: Generated projects use UV + hatchling by default, including PEP 735 dependency groups, `uv sync`, `uv run`, and `uv build`.
- **`--manager poetry` flag**: Explicitly opt in to Poetry-based project generation.

---

## Migration: Repository Build System

The `generate-project` package itself has been migrated from Poetry to UV:

| Area | Before | After |
|------|--------|-------|
| Build backend | `poetry-core` | `hatchling` |
| Dependency file | `poetry.lock` | `uv.lock` |
| Dependency groups | `[tool.poetry.group.*]` | PEP 735 `[dependency-groups]` |
| Install | `poetry install --with dev,test,...` | `uv sync --all-groups` |
| Run tool | `poetry run <tool>` | `uv run <tool>` |
| Build package | `poetry build` | `uv build` |
| Publish | `poetry publish` | `uv publish` |

---

## Improvements

### Developer Experience
- Added `lint-mypy`, `lint-flake8`, `lint-pylint` Makefile targets for running individual linters (applied to root project and both templates).
- Added `test-manual` Makefile target (`uv run pytest -m manual`) to run manually-marked tests (applied to root project and both templates).
- Fixed `make test-cov` module path (`--cov=src/generate_project`) to eliminate spurious "never imported" warnings.
- Fixed `make coverage` error caused by template files being parsed as Python source — added `omit` config for `src/generate_project/templates/*`.

### CI/CD
- Added main branch guard to all three `release.yml` files (root, UV template, Poetry template): tags not on `main` are rejected with a clear error message.
- Migrated all three GitHub Actions workflows (`tests.yml`, `release.yml`, `docs.yml`) to UV.
- Added `pull-requests: write` permission to `docs.yml` to allow PR comments with documentation preview links.
- Poetry is installed in `tests.yml` so that Poetry template tests continue to run in CI.
- Fixed `docs.yml` Build Output check to handle missing `_build/html` directory gracefully.
- Fixed `docs/Makefile` — `poetry run` references were missed during the initial migration.

### Formatting / Tooling
- Set `lines_after_imports = 1` in isort config to align with black 26.1.0's formatting rules (resolves isort/black conflict on module-level variable assignments).

---

## Upgrade Notes

If you use the `generate-project` CLI:
- No changes to the CLI interface, except the default package manager is now UV.
- To preserve existing behavior, add `--manager poetry` to your commands or set `package_manager: poetry` in your `config.yaml`.

If you develop `generate-project` itself:
- Run `uv sync --all-groups` instead of `poetry install --with dev,test,lint,typing,docs`.
- Use `uv run <tool>` instead of `poetry run <tool>`.
- See the updated [CLAUDE.md](CLAUDE.md) for the full development workflow.
- 


## [1.3.0] - 2026-02-20

# Release v1.3.0 - UV Package Manager Support and Release Script Improvements

### New Features
- ✨ Add UV template and `--manager` flag for package manager selection (Poetry or UV)
- ✨ Add interactive prompts and `--no-interactive` flag to release script
- ✨ Replace `--verbose` with `--log` flag in release script
- ✨ Add pre-release combination targets for all stable levels

### Bug Fixes
- 🐛 Fix pre-release bump when finalizing from dev release (PEP 440 compliance)
- 🐛 Fix shell quoting, env cleanup, and Python 3.10 compat in `run.sh`
- 🐛 Remove invalid caret prefix from `python-version` in CI workflows
- 🐛 Fix `project_name` for CLI entry point and pip install in templates
- 🐛 Check all file conflicts before moving generated project files
- 🐛 Only install core deps during UV project generation
- 🐛 Handle missing `tomli` gracefully in `update_versions.py`
- 🐛 Improve venv/conda handling and add `venv-clean` target
- 🐛 Compare against HEAD in `get:python:files:diff`
- 🐛 Fix skip lint-diff and format-diff when no files changed

### Refactoring
- ♻️ Encapsulate rollback state in `RollbackState` class
- ♻️ Extract and nest `bump_version` into dedicated helper closures
- ♻️ Replace print calls with logger and improve error messages
- ♻️ Thread interactive flag through changelog, commit, and tag functions
- ♻️ Remove duplicate metadata from `[tool.poetry]` sections

### CI/CD
- 🚀 Add retry logic to ReadTheDocs API activation step
- 🚀 Use tool-agnostic token env vars and strict publish in release workflows

### Tests
- ✅ Add exhaustive `bump_version` matrix tests (2005 parametrized cases)
- ✅ Add expected-value regression tests for key bump scenarios

### Documentation
- 📝 Update documentation for UV support and fix stale `python_version` references
- 📝 Use `project_name` for distribution references in template docs




## [1.2.1] - 2026-02-08

# Release v1.2.1 - Config and Generate Command Fixes

## Overview

This patch release fixes several bugs in the `config` and `generate` commands, improving argument handling, error safety, and code quality.

## Bug Fixes

### Config Command
- **Fix crash on empty config.yaml**: `yaml.safe_load()` returning `None` for an empty file no longer causes an `AttributeError`
- **Fix config writing all defaults**: Running `config --author_name "John"` now only writes the provided value instead of dumping all cookiecutter defaults to `config.yaml`
- **Show help when no args provided**: `generate-project config` with no arguments now displays help instead of silently writing defaults

### Generate Command
- **Fix extra args leaking to cookiecutter**: Internal args (`command`, `is_library`) were being passed through to cookiecutter as template variables
- **Fix broad exception handling**: Narrowed a catch-all `except Exception` to `subprocess.CalledProcessError` when adding git remote
- **Remove unreachable code**: Removed dead `--secrets requires --github` warning that could never trigger

### Code Quality
- **Fix typos**: `read_ymal_file` → `read_yaml_file`, `missing_enviroment_secrets` → `missing_environment_secrets`
- **Simplify `update_config_file`**: Removed redundant filtering logic and unused parameter

## CLI Changes

The following non-functional or misleading CLI options have been removed:

| Removed Option | Reason | Alternative |
|---------------|--------|-------------|
| `config --project_type` | Was ignored by generate command | Use `generate --library` |
| `config --project_name` | Should not have a default value | Positional arg in generate |
| `generate --project_type` | Was silently overwritten | Use `generate --library` |

## Upgrade Notes

- If you used `generate-project config --project_type library`, use `generate-project generate --library` instead
- The `config.yaml` file format is unchanged; existing configurations will continue to work


## [1.2.0] - 2026-02-06

# Release v1.2.0 - Library vs Application Support

## Overview

This release introduces the ability to generate either **library** or **application** projects, giving users more flexibility in project structure and configuration.

## New Features

### `--library` Flag

Generate library projects with the new `--library` flag:

```bash
# Create an application project (default)
generate-project generate my-app

# Create a library project
generate-project generate my-lib --library
```

### Project Type Differences

| Aspect | Application | Library |
|--------|-------------|---------|
| Entry Point | CLI script in `pyproject.toml` | No entry point |
| Main Module | `main.py` with CLI | Core library modules only |
| Documentation | CLI usage examples | Python import examples |
| Quick Start | `pip install` + CLI command | Python import code |

## Changes

### Features
- Add `--library` flag for library vs application projects

### Documentation
- Adapt documentation templates for app vs library projects
- Update app Quick Start to show CLI usage instead of Python import

### Tests
- Add comprehensive tests for library vs application project types

## Upgrade Notes

This is a backward-compatible release. Existing behavior is preserved - projects generated without the `--library` flag will continue to be application projects with CLI entry points.


## [1.1.1] - 2026-02-05

 ### Changes
 - ✨ feat: add --version option to CLI
- 📝 docs: add documentation for --version option
- 🐛 fix: correct GitHub Actions script context in docs workflow
- 🐛 fix: search for .env file from current working directory


## [1.1.0] - 2025-12-23

### New Features:
✨ Support for `.` as project name: Generate project files directly in the current directory without creating a subdirectory   
✨ Local environment file option: New `--local-env` flag to create a project-specific `.env` file with authentication tokens for manual publishing workflows

### CI/CD Enhancements:
🚀 Added pull_request trigger to test workflows for automatic PR testing   
🔧 Added VS Code configuration to root project for improved developer experience

### Documentation Improvements:
📝 Added CLAUDE.md integration guide to project template for Claude Code users   
📝 Enhanced reference documentation with comprehensive `v1.1.0` features and examples   
📝 Improved publishing setup documentation and command examples   
📝 Improved command `--help` with context-specific help epilogs   


## [1.0.2.post1] - 2025-07-09

 ### Changes
- Add detailed documentation
- Force documentation github check
- Fix module import issue when running tests locally


## [1.0.2] - 2025-07-06

 ### Changes
- Fix generate command flags
- Add toml type stub


## [1.0.1.post3] - 2025-07-04

 ### Changes
- Include template folder in the generated package


## [1.0.1.post2] - 2025-07-04

 ### Changes
- First version
