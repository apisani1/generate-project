# Roadmap to v2.0.0 - Generate Project

This document describes the planned releases to reach v2.0.0 of generate-project.

## Overview

The main goal of v2.0.0 is to:
- Offer the option to use UV or Poetry as package and dependency manager
- Migrate the generate-project itself to UV
- Support both library and application project types

## Current Status

- **Current Version**: v1.0.2.post1
- **Package Manager**: Poetry
- **Template Type**: Poetry-based application template

## Release Sequence

### v1.1.0 - Modernize Project and Template

**Goal**: Update both the generate-project repository and the cookiecutter Poetry template to use the latest scripts, workflows, and tooling.

**Changes to Project Files**

Using the following repo as a reference:

https://github.com/apisani1/mcp-multi-server

Update the following files in the generate-project repository:

- `.github/workflows/delete_workflows_runs.yml` (new file)
- `.github/workflows/docs.yml`
- `.github/workflows/release.yml`
- `.github/workflows/tests.yml`
- `.github/workflows/update_rtd.yml`
- `.gitignore`
- `.pypirc`
- `.readthedocs.yaml`
- `.vscode/launch.json`
- `.vscode/settings.json`
- `.vscode/tasks.json`
- `Makefile` (adapt for application vs library differences)
- `pyproject.toml` (adapt for application vs library differences)
- `run.sh` (adapt for application vs library differences)
- `scripts/release.py`
- `scripts/reset_version.py`
- `scripts/update_versions.py`

**Changes to Template Files**:

Apply the same updates to the cookiecutter template files:

`src/generate_project/templates/poetry-template/{{cookiecutter.project_name}}/`
- `.github/workflows/delete_workflows_runs.yml` (new)
- `.github/workflows/docs.yml`
- `.github/workflows/release.yml`
- `.github/workflows/tests.yml`
- `.github/workflows/update_rtd.yml`
- `.gitignore`
- `.pypirc`
- `.readthedocs.yaml`
- `.vscode/launch.json`
- `.vscode/settings.json`
- `.vscode/tasks.json`
- `Makefile`
- `pyproject.toml`
- `run.sh`
- `scripts/release.py`
- `scripts/reset_version.py`
- `scripts/update_versions.py`

**Important Considerations**:
- Be mindful of Jinja2 syntax in cookiecutter templates
- Pay special attention to escaping in GitHub workflow files
- Adapt application-specific configurations when needed
- Note differences between library (mcp-multi-server) and application(generate-project) patterns

**Testing Requirements**:
- Update test suite to verify new workflow files
- Test template generation with new files
- Verify GitHub Actions workflows validate correctly
- Test release script functionality

**Documentation Updates**:
- Update README.md with any new features
- Update CLAUDE.md with new development commands
- Document any breaking changes
- CHANGELOG.md will be automatically update by scripts/release.py

---

### v1.2.0 - Add Library vs Application Support

**Goal**: Enable generate-project to create either library or application projects with appropriate configurations.

**New Features**:

Add `--library` flag to `generate-project generate` command:

```bash
# Create an application project (default)
generate-project generate my-app

# Create a library project
generate-project generate my-lib --library
```

**Configuration Differences**:

| Aspect | Application | Library |
|--------|-------------|---------|
| Entry Point | CLI/script in pyproject.toml | No entry point |
| Main Module | `main.py` with CLI | Core library modules only |
| Dependencies | May include CLI tools (click, typer) | Minimal dependencies |
| Scripts | Application-specific scripts | Library build scripts |
| Documentation Focus | User guides, CLI reference | API documentation |
| Testing Approach | Integration + unit tests | Primarily unit tests |
| Packaging | May include data files, assets | Code + type stubs |

**Implementation Details**:
- Add `project_type` parameter to cookiecutter.json (default: "application")
- Create conditional blocks in templates using Jinja2
- Adjust pyproject.toml structure based on type
- Customize README and documentation structure
- Adapt test structure and examples

**Template Changes**:
- Conditional `[tool.poetry.scripts]` section
- Different example code in `src/{{cookiecutter.package_name}}/`
- Adjusted documentation templates
- Different testing patterns

**Testing Requirements**:
- Test both application and library project generation
- Verify correct file structure for each type
- Test that generated projects pass their own test suites
- Validate pyproject.toml structure for both types

**Documentation Updates**:
- Document `--library` flag in README
- Add examples of library vs application projects
- Update CLAUDE.md with new template structure
- Add migration guide for existing users

---

### v1.3.0 - Add UV Template Support

**Goal**: Provide a UV-based template as an alternative to Poetry, giving users choice of package manager.

**New Features**:

Add `--manager` option to `generate-project generate` command:

```bash
# Use Poetry (for backward compatibility, this release keeps Poetry as default)
generate-project generate my-project --manager poetry

# Use UV  
generate-project generate my-project --manager uv
```

**Implementation Details**:

1. **Create UV Template**:
   - Copy `src/generate_project/templates/poetry-template/` to `src/generate_project/templates/uv-template/`
   - Migrate all Poetry commands to UV equivalents
   - Update `pyproject.toml` for UV compatibility
   - Migrate `run.sh` script commands to UV
   - Update GitHub Actions workflows to use UV
   - Adapt ReadTheDocs configuration for UV

2. **Template Selection Logic**:
   - Update `main.py` to select template based on `--manager` flag
   - Default to `poetry` in this release (changed to `uv` in v2.0.0)
   - Validate manager parameter

3. **Command Equivalents**:

| Task | Poetry | UV |
|------|--------|-----|
| Install deps | `poetry install` | `uv sync` |
| Add dependency | `poetry add pkg` | `uv add pkg` |
| Run command | `poetry run cmd` | `uv run cmd` |
| Build | `poetry build` | `uv build` |
| Publish | `poetry publish` | `uv publish` |
| Shell | `poetry shell` | `uv shell` (if available) |

4. **Configuration Files**:
   - UV uses `pyproject.toml` natively (no separate config file)
   - Adjust lock file handling (`poetry.lock` vs `uv.lock`)
   - Update `.gitignore` for UV-specific files

**Testing Requirements**:
- Test project generation with both `--manager poetry` and `--manager uv`
- Verify UV template generates valid pyproject.toml
- Test that generated UV projects can install dependencies
- Verify all run.sh commands work with UV
- Test GitHub Actions workflows with UV

**Documentation Updates**:
- Document `--manager` option in README
- Add UV template documentation
- Create comparison guide: Poetry vs UV
- Update CLAUDE.md with UV development commands
- Add troubleshooting section for UV-specific issues

---

### v2.0.0 - Migrate to UV and Make UV Default

**Goal**: Complete the transition to UV as the primary package manager for both generate-project itself and newly generated projects.

**Major Changes**:

1. **Migrate generate-project Repository to UV**:
   
   Convert the following files to use UV:
   - `.github/workflows/docs.yml`
   - `.github/workflows/release.yml`
   - `.github/workflows/tests.yml`
   - `.github/workflows/update_rtd.yml`
   - `.readthedocs.yaml`
   - `.vscode/launch.json`
   - `.vscode/settings.json`
   - `.vscode/tasks.json`
   - `Makefile`
   - `pyproject.toml`
   - `run.sh`
   - `scripts/release.py`
   - `scripts/reset_version.py`
   - `scripts/update_versions.py`

2. **Change Default Template**:
   - Change default `--manager` from `poetry` to `uv`
   - Update user configuration defaults

3. **Remove Poetry Development Dependencies**:
   - Uninstall Poetry from development environment
   - Remove Poetry-specific scripts
   - Update documentation to use UV commands

**Migration Strategy**:
- Provide migration guide for contributors
- Document breaking changes clearly
- Provide rollback instructions if needed

**Testing Requirements**:
- Full test suite must pass with UV
- Test both UV and Poetry template generation
- Verify CI/CD pipelines work with UV
- Test release process with UV
- Validate documentation builds with UV

**Documentation Updates**:
- Rewrite README.md to feature UV primarily
- Update all code examples to UV syntax
- Revise CLAUDE.md for UV development workflow
- Create "Migrating from Poetry to UV" guide
- Add FAQ section for UV-related questions

**Breaking Changes**:
- Default package manager changes from Poetry to UV
- Development workflow changes for contributors
- Some environment setup steps will differ
- Lock file format changes (poetry.lock → uv.lock)

**Backward Compatibility**:
- Project geberation based on poetry template remains available via `--manager poetry`
- Existing generated projects not affected
- Old workflows continue to work

---

## Success Criteria

Each release must meet these criteria before proceeding to the next:

1. **All tests pass**: Both project tests and generated project tests
2. **Documentation updated**: README, CLAUDE.md, and inline docs current
3.  **CI/CD working**: All GitHub Actions workflows pass
4. **Manual testing**: Generate and test both library and application projects
5. **Backward compatibility**: Existing functionality preserved where applicable

---

## Notes for Claude Code Implementation

When implementing each release with Claude Code:

1. **Work incrementally**: Implement one file type at a time
2. **Test frequently**: Run tests after each significant change
3. **Check templates**: Verify Jinja2 syntax in cookiecutter templates
4. **Validate workflows**: Test GitHub Actions locally when possible
5. **Document changes**: Update CLAUDE.md as you go
6. **Ask for clarification**: When file differences between mcp-multi-server (library) and generate-project (application) are unclear

## Reference Materials

- **mcp-multi-server repository**: Source for latest patterns (library-focused)
- **Current generate-project**: Baseline for application patterns
- **Poetry documentation**: For maintaining Poetry template
- **UV documentation**: For implementing UV template
- **Cookiecutter documentation**: For template best practices
