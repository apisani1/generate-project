# Changelog

## [1.3.0rc1] - 2026-02-17

## Release Candidate v1.3.0 - UV Package Manager Support and Release Script Improvements

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


## [1.2.0b2] - 2026-02-06

 ### Changes
- 📝 docs: update app Quick Start to show CLI usage instead of Python import



## [1.2.0b1] - 2026-02-06

 ### Changes
- 📝 docs: adapt documentation templates for app vs library projects
- ✅ test: add tests for library vs application project types
- ✨ feat: add --library flag for library vs application projects



## [1.1.1] - 2026-02-05

 ### Changes
- 📝 docs: add documentation for --version option


## [1.1.1rc2] - 2026-02-05

 ### Changes
- 🐛 fix: correct GitHub Actions script context in docs workflow



## [1.1.1rc1] - 2026-02-05

 ### Changes
- ✨ feat: add --version option to CLI
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


## [1.0.3rc11] - 2025-12-19

 ### Changes
- 📝 docs: add context-specific help epilogs for CLI commands
- ♻️ refactor: consolidate credential file creation into generic function



## [1.0.3rc10] - 2025-12-19

 ### Changes
- 🐛 fix: resolve FileNotFoundError in project generation



## [1.0.3rc9] - 2025-12-18

 ### Changes
- fix: add template documentation and fix bash syntax errors
- feat: implement tool-agnostic credential management



## [1.0.3rc7] - 2025-12-16

 ### Changes
- 🐛 fix: add v2 prefix to Poetry cache keys to force invalidation
- 🐛 fix: include poetry.lock in CI cache key for proper invalidation
- 🐛 fix: add roman package for Sphinx/Python 3.13 compatibility


## [1.0.3rc6] - 2025-12-15

 ### Changes
- ♻️ refactor: simplify publishing instructions output



## [1.0.3rc5] - 2025-12-15

 ### Changes
- 💄 style: improve color consistency in terminal output



## [1.0.3rc4] - 2025-12-15

 ### Changes
- refactor: simplify GitHub repository ownership check



## [1.0.3rc3] - 2025-12-15

 ### Changes
- 🐛 fix: improve error message when directory already exists



## [1.0.3rc2] - 2025-12-15

 ### Changes
- 🐛 fix: prevent crash when GitHub repository already exists



## [1.0.3rc1] - 2025-12-15

 ### Changes
- feat: activate ReadTheDocs for all version tags
- feat: modernize project with PEP 621 dual format (root + template)
  


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
- Add test suite
- Add user configuration file


## [1.0.1.post1] - 2025-07-03

 ### Changes
- Update README.md



## [1.0.1] - 2025-07-02

 ### Changes
- First release


## [1.0.0] - 2025-07-02

 ### Changes
- First release


## [0.1.0] - 2025-07-02

 ### Changes
- First release


## [0.1.0] - 2025-07-02

 ### Changes
- First version

