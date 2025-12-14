# Implementation Plan: generate-project v1.1.0 to v2.0.0

## Overview

This plan covers the sequential implementation of four releases to modernize generate-project, add library/application support, add UV template support, and migrate to UV as the default package manager.

**Timeline Estimate**: 11-15 days
- v1.1.0: 2-3 days (modernization)
- v1.2.0: 2-3 days (library/app support)
- v1.3.0: 4-5 days (UV template)
- v2.0.0: 3-4 days (UV migration)

## Current Architecture

- **Version**: 1.0.2.post1
- **CLI**: argparse-based with `generate` and `config` commands
- **Entry point**: `src/generate_project/main.py`
- **Template**: `src/generate_project/templates/poetry-template/`
- **Config system**: `cookiecutter.json` (global) + `config.yaml` (user)
- **Dynamic CLI args**: Built via `build_menu_from_config()` function
- **Testing**: pytest-cookies with `bake_in_temp_dir()` fixtures

## Reference Repository

**Location**: `/Users/antonio/AI/MyCode/mcp-multi-server`
- Library project with sophisticated patterns
- Advanced release.py with PEP 440 versioning
- Comprehensive workflows and scripts
- Must adapt library patterns for application needs

---

# v1.1.0 - Modernize Project and Template

**Goal**: Update project and template files to adopt mcp-multi-server patterns

## Key Changes

### Project Root Updates

**New File**:
- `.github/workflows/delete_workflow_runs.yml` - Workflow cleanup utility

**Enhanced Files**:
1. `.github/workflows/docs.yml`
   - Add doc8 quality checks
   - Add sphinx linkcheck validation
   - Add artifact uploads for PR previews
   - Add PR comments with documentation preview links

2. `.github/workflows/release.yml`
   - Add version type detection (stable vs prerelease vs dev)
   - Add conditional PyPI publishing (stable only)
   - Add conditional RTD updates (stable only)
   - Add release summary output

3. `scripts/release.py`
   - Replace with sophisticated version from mcp-multi-server
   - Add PEP 440 versioning support (major/minor/micro/alpha/beta/rc/dev/post)
   - Add CHANGELOG.md automation
   - Add rollback capability

4. `scripts/update_versions.py`
   - Ensure updates all version locations
   - Support tomllib (Python 3.11+) with tomli fallback

5. `scripts/reset_version.sh`
   - Update to match reference implementation

**Critical Adaptations**:
- **KEEP** `[tool.poetry.scripts]` in pyproject.toml (application marker)
- **KEEP** `include = ["src/generate_project/templates/**/*"]` (template bundling)
- **KEEP** cookiecutter exclusions in all tool configs (black, flake8, mypy, pylint, isort)
- **REMOVE** MCP-specific and Prolog-specific content

### Template Updates

**Location**: `src/generate_project/templates/poetry-template/{{cookiecutter.project_name}}/`

Apply same changes as project root, but with Jinja2 variables:
- Replace project names with `{{ cookiecutter.project_name }}`
- Replace package names with `{{ cookiecutter.package_name }}`
- Replace Python versions with `{{ cookiecutter.python_version }}`
- Maintain cookiecutter exclusions in tool configs

## Implementation Steps

1. **Copy new files from reference**:
   - `.github/workflows/delete_workflow_runs.yml`

2. **Update workflows**:
   - Compare and merge docs.yml, release.yml, tests.yml
   - Preserve generate-project specific configurations

3. **Update scripts**:
   - Copy release.py, update_versions.py, reset_version.sh
   - Replace 'mcp_multi_server' with 'generate_project'

4. **Apply to template**:
   - Replicate all changes in template directory
   - Add Jinja2 variables where needed

5. **Update tests**:
   - Verify new files exist in test_structure.py
   - Add workflow YAML validation in test_github.py

## Critical Files

- `/Users/antonio/AI/MyCode/mcp-multi-server/scripts/release.py` (reference)
- `/Users/antonio/AI/MyCode/generate-project/scripts/release.py` (update)
- `/Users/antonio/AI/MyCode/generate-project/.github/workflows/release.yml` (update)
- `/Users/antonio/AI/MyCode/generate-project/src/generate_project/templates/poetry-template/{{cookiecutter.project_name}}/pyproject.toml` (update with variables)

## Testing

1. Run `make test` - all tests pass
2. Generate project: `generate-project test-v110`
3. In generated project: `make check`, `make docs`, `make build`
4. Test release.py: `python scripts/release.py create micro --changes "test"`
5. Validate workflows with actionlint (if available)

## Risks & Mitigation

- **Risk**: Breaking cookiecutter exclusions
  - **Mitigation**: Test lint/format on template directory
- **Risk**: Breaking application entry point
  - **Mitigation**: Keep `[tool.poetry.scripts]` section intact
- **Risk**: GitHub workflow syntax errors
  - **Mitigation**: Validate YAML, test in GitHub Actions

---

# v1.2.0 - Add Library vs Application Support

**Goal**: Enable generation of both library and application projects

## Key Changes

### Configuration

**Update** `cookiecutter.json` (both templates):
```json
{
    "project_type": "application",  // NEW: default to application
    // ... existing fields
}
```

**Update** `config.yaml`:
```yaml
default_context:
  project_type: "application"  // NEW: save user preference
  // ... existing fields
```

### CLI Updates

**Update** `src/generate_project/main.py` (lines ~481-484):

Add mutually exclusive flags:
```python
project_type_group = generate_parser.add_mutually_exclusive_group()
project_type_group.add_argument(
    "--application",
    dest="project_type",
    action="store_const",
    const="application",
    help="Generate application project (default, has CLI entry point)"
)
project_type_group.add_argument(
    "--library",
    dest="project_type",
    action="store_const",
    const="library",
    help="Generate library project (no CLI entry point)"
)
```

Set default if not specified (lines ~543-557):
```python
if not hasattr(args, 'project_type') or args.project_type is None:
    args.project_type = "application"  # Default
```

### Template Conditionals

**Update** `poetry-template/{{cookiecutter.project_name}}/pyproject.toml`:

```toml
{% if cookiecutter.project_type == "application" %}
[tool.poetry.scripts]
{{ cookiecutter.package_name }} = "{{ cookiecutter.package_name }}.main:main"
{% endif %}
```

**Conditional files** (via cookiecutter hooks or Jinja2):
- `src/{{cookiecutter.package_name}}/main.py` - Only for applications
- Different README examples for library vs application
- Different documentation structure

## Implementation Steps

1. **Add project_type to cookiecutter.json**
2. **Update main.py CLI**:
   - Add --application and --library flags
   - Add default logic
3. **Add conditionals to template**:
   - pyproject.toml `[tool.poetry.scripts]` section
   - Conditional main.py file
4. **Update config.yaml schema**
5. **Create tests**: `tests/test_project_type.py`
6. **Add fixtures**: Update `tests/conftest.py`

## Critical Files

- [src/generate_project/main.py](src/generate_project/main.py) (lines 481-484, 543-557)
- [src/generate_project/templates/poetry-template/cookiecutter.json](src/generate_project/templates/poetry-template/cookiecutter.json)
- [src/generate_project/templates/poetry-template/{{cookiecutter.project_name}}/pyproject.toml](src/generate_project/templates/poetry-template/{{cookiecutter.project_name}}/pyproject.toml)
- [tests/test_project_type.py](tests/test_project_type.py) (new)
- [tests/conftest.py](tests/conftest.py)

## Testing

**New test file**: `tests/test_project_type.py`
```python
def test_application_project_has_entry_point(cookies)
def test_library_project_no_entry_point(cookies)
def test_cli_application_flag(cookies)
def test_cli_library_flag(cookies)
def test_config_saves_project_type(cookies)
```

**New fixtures** in `conftest.py`:
```python
@pytest.fixture
def application_project(cookies):
    """Create application project."""

@pytest.fixture
def library_project(cookies):
    """Create library project."""
```

**Validation**:
1. Default: `generate-project test-app` → application
2. Explicit app: `generate-project test-app --application`
3. Library: `generate-project test-lib --library`
4. Config save: `generate-project config --project_type library`
5. Both types run `make check` successfully

## Risks & Mitigation

- **Risk**: Breaking existing users
  - **Mitigation**: Default is "application" (backward compatible)
- **Risk**: CLI flag conflicts
  - **Mitigation**: Use mutually_exclusive_group
- **Risk**: Jinja2 syntax errors
  - **Mitigation**: Test both branches thoroughly

---

# v1.3.0 - Add UV Template Support

**Goal**: Create UV template and enable template selection

## Key Changes

### New Template Directory

**Create**: `src/generate_project/templates/uv-template/`

Structure (copy from poetry-template, then modify):
```
uv-template/
├── cookiecutter.json
└── {{cookiecutter.project_name}}/
    ├── .github/workflows/ (modified for UV)
    ├── .gitignore (add .venv/, uv.lock)
    ├── .readthedocs.yaml (modified for UV)
    ├── pyproject.toml (UV FORMAT)
    ├── README.md (UV instructions)
    ├── run.sh (UV COMMANDS)
    ├── scripts/ (modified for UV)
    └── ... (rest same as poetry)
```

### UV-Specific Files

**pyproject.toml** - Key differences:
```toml
[project]  # UV uses [project], not [tool.poetry]
name = "{{ cookiecutter.project_name }}"
version = "{{ cookiecutter.version }}"
requires-python = ">={{ cookiecutter.python_version.replace('^', '') }}"
dependencies = []

{% if cookiecutter.project_type == "application" %}
[project.scripts]  # UV uses [project.scripts], not [tool.poetry.scripts]
{{ cookiecutter.package_name }} = "{{ cookiecutter.package_name }}.main:main"
{% endif %}

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.4",
    # ... all dev deps
]
```

**run.sh** - Command equivalents:
- `poetry install` → `uv sync`
- `poetry add pkg` → `uv add pkg`
- `poetry run cmd` → `uv run cmd`
- `poetry build` → `uv build`
- `poetry publish` → `uv publish`

**GitHub workflows** - UV installation:
```yaml
- name: Install UV
  run: |
    curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Install Dependencies
  run: uv sync --all-extras
```

### Configuration Updates

**Update** `cookiecutter.json` (both templates):
```json
{
    "package_manager": "poetry",  // NEW: default to poetry in v1.3.0
    // ... existing fields
}
```

**Update** `src/generate_project/main.py` (lines ~515-516):

Add manager flag:
```python
package_manager_group = generate_parser.add_mutually_exclusive_group()
package_manager_group.add_argument(
    "--manager",
    type=str,
    choices=["poetry", "uv"],
    help="Package manager to use (default: poetry in v1.3.0)"
)
```

Template selection (lines ~548-549):
```python
# Determine package manager
if hasattr(args, 'manager') and args.manager:
    package_manager = args.manager
else:
    package_manager = "poetry"  # Default in v1.3.0

# Set template path
if args.template_path is None:
    template_name = f"{package_manager}-template"
    args.template_path = Path(__file__).parent / "templates" / template_name

    if not args.template_path.exists():
        print_colored(f"Error: Template not found: {template_name}", Colors.RED)
        sys.exit(1)
```

### Package Updates

**Update** `pyproject.toml`:
```toml
include = [
    "src/generate_project/templates/poetry-template/**/*",
    "src/generate_project/templates/uv-template/**/*",  # NEW
    "src/generate_project/templates/config.yaml"
]
```

## Implementation Steps

1. **Create uv-template directory**:
   - Copy poetry-template structure
   - Modify pyproject.toml to UV format
   - Update run.sh with UV commands
   - Update GitHub workflows for UV
   - Update README with UV instructions

2. **Add package_manager to cookiecutter.json** (both templates)

3. **Update main.py**:
   - Add --manager flag
   - Add template selection logic

4. **Update config.yaml schema**

5. **Update pyproject.toml includes**

6. **Create tests**: `tests/test_uv_template.py`

7. **Add UV fixtures** to `tests/conftest.py`

## Critical Files

- [src/generate_project/templates/uv-template/](src/generate_project/templates/uv-template/) (entire new directory)
- [src/generate_project/templates/uv-template/{{cookiecutter.project_name}}/pyproject.toml](src/generate_project/templates/uv-template/{{cookiecutter.project_name}}/pyproject.toml) (UV format)
- [src/generate_project/templates/uv-template/{{cookiecutter.project_name}}/run.sh](src/generate_project/templates/uv-template/{{cookiecutter.project_name}}/run.sh) (UV commands)
- [src/generate_project/main.py](src/generate_project/main.py) (template selection, lines 515-516, 548-549)
- [pyproject.toml](pyproject.toml) (update includes)
- [tests/test_uv_template.py](tests/test_uv_template.py) (new)

## Testing

**New test file**: `tests/test_uv_template.py`
```python
def test_uv_template_generation(cookies)
def test_uv_template_application_vs_library(cookies)
def test_cli_manager_flag(cookies)
def test_combined_flags(cookies)  # --library --manager uv
```

**Validation**:
1. Default: `generate-project test-default` → poetry template
2. UV selection: `generate-project test-uv --manager uv` → uv template
3. Combined: `generate-project test-lib --library --manager uv`
4. UV project works: `cd test-uv && uv sync && uv run pytest`
5. Both templates included in built package

## Risks & Mitigation

- **Risk**: UV template syntax errors
  - **Mitigation**: Test thoroughly, generate and run UV project
- **Risk**: Template not in package
  - **Mitigation**: Update pyproject.toml includes, verify in dist/
- **Risk**: Platform compatibility
  - **Mitigation**: Test on Linux, macOS, Windows via CI

---

# v2.0.0 - Migrate to UV and Make UV Default

**Goal**: Migrate generate-project itself to UV and change default to UV

## Key Changes

### Migrate Project to UV

**Update** `pyproject.toml` - Convert Poetry → UV format:

**Before** (Poetry):
```toml
[tool.poetry]
name = "generate-project"
version = "1.3.0"
[tool.poetry.dependencies]
python = "^3.10"
[tool.poetry.group.test.dependencies]
pytest = "^7.4.4"
```

**After** (UV):
```toml
[project]
name = "generate-project"
version = "2.0.0"
requires-python = ">=3.10"
dependencies = [
    "cookiecutter>=2.6.0",
    "python-dotenv>=1.1.0",
    "pyyaml>=6.0.0",
]

[project.scripts]
generate-project = "generate_project.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.4",
    "pytest-cookies>=0.7.0",
    # ... all dev deps
]

# Keep all [tool.*] configs (black, mypy, flake8, etc.)
```

**Update** `run.sh`:
- Replace all `poetry` commands with `uv` equivalents

**Update** `.github/workflows/*.yml` (4 files):
- Install UV instead of Poetry
- Use `uv sync` instead of `poetry install`
- Use `uv run` instead of `poetry run`
- Use `uv build` instead of `poetry build`

**Update** documentation:
- README.md - UV installation instructions
- CLAUDE.md - UV development commands
- docs/ - UV usage

### Change Default to UV

**Update** `src/generate_project/main.py` (line ~548):
```python
# Change default from "poetry" to "uv"
if hasattr(args, 'manager') and args.manager:
    package_manager = args.manager
else:
    package_manager = "uv"  # CHANGED: Default to UV in v2.0.0
```

**Update** `cookiecutter.json` (both templates):
```json
{
    "package_manager": "uv",  // CHANGED: Default to UV in v2.0.0
    // ...
}
```

## Implementation Steps

1. **Migrate project to UV**:
   - Convert pyproject.toml to UV format
   - Update run.sh with UV commands
   - Update GitHub workflows
   - Update documentation

2. **Change defaults**:
   - Update main.py default to "uv"
   - Update cookiecutter.json default to "uv"

3. **Test migration**:
   - `uv sync` - Install dependencies
   - `uv run pytest tests/` - Run tests
   - `uv build` - Build package
   - `uv run generate-project --help` - Verify CLI

4. **Test both templates**:
   - Generate UV project (default)
   - Generate Poetry project (--manager poetry)

5. **Update documentation**:
   - Add migration guide
   - Update all examples to UV
   - Add "Using Poetry" section

## Critical Files

- [pyproject.toml](pyproject.toml) (convert to UV format)
- [run.sh](run.sh) (UV commands)
- [.github/workflows/tests.yml](.github/workflows/tests.yml) (UV installation)
- [.github/workflows/release.yml](.github/workflows/release.yml) (UV build/publish)
- [src/generate_project/main.py](src/generate_project/main.py) (change default, line ~548)
- [README.md](README.md) (UV documentation)
- [CLAUDE.md](CLAUDE.md) (UV development commands)

## Testing

**Migration validation**:
1. `uv sync` - Install with UV
2. `uv run pytest tests/` - All tests pass
3. `uv build` - Build succeeds
4. `uv run generate-project --help` - CLI works

**Default change validation**:
```python
def test_default_is_uv():
    """Test UV is now default."""
    # Generate without --manager flag
    # Verify uses uv-template

def test_poetry_still_available():
    """Test Poetry still available."""
    # Generate with --manager poetry
    # Verify uses poetry-template
```

**Integration tests**:
1. Generate default: `uv run generate-project test-default`
2. Verify UV template: `cat test-default/pyproject.toml | grep "\[project\]"`
3. Generate Poetry: `uv run generate-project test-poetry --manager poetry`
4. Verify Poetry template: `cat test-poetry/pyproject.toml | grep "\[tool.poetry\]"`

## Risks & Mitigation

- **Risk**: Breaking change for existing users
  - **Mitigation**: v2.0.0 allows breaking changes, clear release notes
- **Risk**: UV compatibility issues
  - **Mitigation**: Test on multiple platforms via CI matrix
- **Risk**: Documentation out of sync
  - **Mitigation**: Search for "poetry" references, update or make generic

---

# Testing Strategy Across All Releases

## Continuous Validation

After each release:
1. Run full test suite: `make test` (Poetry) or `uv run pytest tests/` (UV)
2. Generate test project with default settings
3. Generate test project with all flag combinations
4. Run `make check` in generated projects
5. Verify GitHub workflows validate (YAML syntax)

## Test Progression

**v1.1.0**:
- Test structure: New files exist
- Test GitHub: Workflows validate
- Test release.py: Version bumping works
- Test generated projects: All workflows pass

**v1.2.0**:
- Test project types: Application vs library differences
- Test CLI flags: --application and --library
- Test config: project_type saves and loads
- Test conditionals: Scripts section present/absent correctly

**v1.3.0**:
- Test templates: Both poetry and uv generate
- Test CLI flags: --manager poetry|uv
- Test combinations: --library --manager uv
- Test UV projects: uv sync && uv run pytest works
- Test package: Both templates included in dist/

**v2.0.0**:
- Test migration: All tests pass with UV
- Test defaults: UV is default, Poetry available via flag
- Test CI: GitHub workflows work with UV
- Test documentation: Builds with UV

## Regression Testing

Maintain test matrix across versions:

| Test | v1.1.0 | v1.2.0 | v1.3.0 | v2.0.0 |
|------|--------|--------|--------|--------|
| Default generation | ✓ | ✓ | ✓ | ✓ |
| Application project | ✓ | ✓ | ✓ | ✓ |
| Library project | - | ✓ | ✓ | ✓ |
| Poetry template | ✓ | ✓ | ✓ | ✓ |
| UV template | - | - | ✓ | ✓ |
| Combined flags | - | - | ✓ | ✓ |

---

# Success Criteria

Each release must meet these before proceeding:

1. **All tests pass**: Project tests + generated project tests
2. **Documentation updated**: README, CLAUDE.md, release notes
3. **CI/CD working**: All GitHub Actions workflows pass
4. **Manual testing**: Generate both library and application (where applicable)
5. **Backward compatibility**: Existing functionality preserved (except v2.0.0)

---

# File Change Summary

## v1.1.0
- **Modified**: ~15 project files + ~15 template files
- **New**: delete_workflow_runs.yml
- **Effort**: 2-3 days

## v1.2.0
- **Modified**: 3 core files + 2 template files + 2 test files
- **New**: test_project_type.py
- **Effort**: 2-3 days

## v1.3.0
- **New directory**: uv-template (~30 files)
- **Modified**: 3 core files + 2 test files
- **New**: test_uv_template.py
- **Effort**: 4-5 days

## v2.0.0
- **Modified**: 9 project files
- **Updated**: Documentation (3-4 files)
- **Effort**: 3-4 days

**Total**: ~70 files across all releases, 11-15 days

---

# Implementation Notes

## Key Principles

1. **Sequential implementation**: Must complete in order (v1.1.0 → v1.2.0 → v1.3.0 → v2.0.0)
2. **Test after each change**: Don't accumulate untested changes
3. **Application vs Library**: Always maintain application-specific configs
4. **Template integrity**: Test cookiecutter exclusions don't break
5. **Both templates work**: After v1.3.0, both Poetry and UV must work

## Critical Reminders

- **NEVER remove** `[tool.poetry.scripts]` from application pyproject.toml
- **ALWAYS keep** cookiecutter exclusions in tool configs
- **TEST both branches** of conditional Jinja2 templates
- **VERIFY package includes** both templates after v1.3.0
- **DOCUMENT breaking changes** clearly in v2.0.0 release notes

## Next Steps

1. Start with v1.1.0 implementation
2. Focus on one file at a time
3. Run tests frequently
4. Generate test projects to verify
5. Move to next release only after current passes all criteria
