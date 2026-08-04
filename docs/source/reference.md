# Command Reference

This is the reference guide for generate-project, a command-line tool for generating Python project folders with pre-configured development tasks for formatting, linting, documentation, testing, release management and CI/CD.

## Commands Overview

generate-project provides three commands:

- **generate**: Create a new Python project folder with configurable parameters
- **config**: Configure default project parameters
- **install-skills**: Install the bundled Claude Code commands/skill into a `.claude` directory

For quick help use:
```bash
generate-project --help
generate-project --version
generate-project generate --help
generate-project config --help
generate-project install-skills --help
```

## Global Options

| Option | Description |
|--------|-------------|
| `--help` | Show help message and exit |
| `--version` | Show program version and exit |

## generate Command

Create a new Python project folder with comprehensive development setup.

### Synopsis

```bash
generate-project generate PROJECT_NAME [OPTIONS]
```

### Arguments

#### Required Arguments

| Argument | Description |
|----------|-------------|
| `PROJECT-NAME` | Name of the project to create |

generate-project will create a new subdirectory named  `PROJECT-NAME` in your current working directory and populate it with the project template. If you want to generate the project in an existing directory without creating a subdirectory, use `.` as the project name.

#### Project Configuration Options

These options configure the project metadata and can be saved as defaults using the `config` command:

| Option | Description |
|--------|-------------|
| `--author_name` | Author's full name |
| `--email` | Author's email address |
| `--github_username` | GitHub username for repository creation |
| `--version` | Initial project version number |
| `--description` | Short project description |
| `--python_min_version` | Minimum Python version |
| `--package_name` | Python package name (can be auto-generated from project name) |
| `--autodoc_mock_imports` | Comma-separated list of modules to mock for Sphinx autodoc |
| `--complex_mock_modules` | Comma-separated list of complex modules requiring special mocking |
| `--google_analytics_id` | Google Analytics tracking ID for documentation SEO metrics |

#### Behavior Control Options

| Option | Description | Default |
|--------|-------------|---------|
| `--no-install` | Skip installing dependencies | Install dependencies |
| `--no-git` | Skip Git repository initialization | Initialize Git repository |
| `--install-skills` | Install the bundled Claude Code commands/skill into the new project's `.claude/` | Do not install |

#### Project Type Options

| Option | Description | Default |
|--------|-------------|---------|
| `--library` | Create a library project (no CLI entry point) | Application project |
| `--manager` | Package manager: `uv` or `poetry` | `uv` |
| `--supacode` | Generate a `supacode.json` wiring Supacode's setup/archive/delete worktree hooks to `run.sh`/`make worktree-*` | Not created |

The default UV projects use the hatchling build backend, PEP 621 `[project]` metadata with
`[dependency-groups]` (PEP 735), `astral-sh/setup-uv` in CI, and `uv sync`/`uv run`/`uv
build`/`uv publish` in `run.sh`.

When `--manager poetry` is specified instead:
- Uses the poetry-core build backend
- Uses `[tool.poetry]` metadata and dependency groups
- CI workflows use Poetry instead of `astral-sh/setup-uv`
- `run.sh` uses `poetry install`, `poetry run`, `poetry build`, `poetry publish`

When `--library` is specified:
- No `[project.scripts]` section is added to `pyproject.toml`
- No `main.py` CLI entry point is created
- README focuses on API usage instead of CLI usage

When `--supacode` is specified:
- A `supacode.json` is created, binding Supacode's setup/archive/delete worktree hooks to three
  new `run.sh` commands (also exposed as `make worktree-setup`, `make worktree-archive`,
  `make worktree-delete`)
- `worktree:delete` refuses to run on a dirty tree, on commits reachable from no other ref, or
  when stashes exist on the branch — override with `SUPACODE_FORCE_DELETE=1`
- Each phase also calls an optional `scripts/worktree-<phase>.sh` per-repo hook if present

#### GitHub Integration Options (requires gh CLI)

| Option | Description | Default |
|--------|-------------|---------|
| `--github` | Create a private GitHub repository  | No repository creation |
| `--public` | Create a public GitHub repository | Private repository |
| `--secrets` | Create GitHub repository secrets for PyPl and RTD integration | No secrets creation |

GitHub repository secrets are used by GitHub CI/CD actions and automated publishing tasks:
```bash
    make release-major        # Create major release
    make release-minor        # Create minor release
    make release-micro        # Create micro (patch) release
    make release-rc           # Create release candidate
    make release-beta         # Create beta pre-release
    make release-alpha        # Create alpha pre-release
```


#### Manual Publishing Setup Options

| Option | Description | Default |
|--------|-------------|---------|
| `--local-env` | Create local `.env` file with tokens in project directory | No .env creation |

This local `.env` file will be used for manual publishing tasks:
```bash
    make publish-test         # Publish to TestPyPI
    make publish              # Publish to PyPI
```

#### File Path Options

| Option | Description | Default |
|--------|-------------|---------|
| `--env` | Path to .env file containing tokens for repository secrets | `.env` with location auto-detect|
| `--template` | Path to custom cookiecutter template | Built-in template (selected by `--manager`) |

### Examples

#### Basic Project Creation

```bash
generate-project generate my-project
```

#### Custom Project with Metadata

```bash
generate-project generate my-project \
    --author_name="John Doe" \
    --email="john@example.com" \
    --description="An awesome Python library"
```

#### Full Setup with GitHub and Publishing

```bash
generate-project generate my-project \
    --author_name="John Doe" \
    --email="john@example.com" \
    --github_username="johndoe" \
    --public \
    --secrets \
```

#### Create UV Project

```bash
generate-project generate my-project --manager uv
```

#### Using Custom Template

```bash
generate-project generate my-project \
    --template="/path/to/custom/template" \
    --author_name="John Doe"
```

#### Generate Project in Current Directory

```bash
# Navigate to your project directory first
cd my-project

# Generate project files in current directory
generate-project generate .
```

This approach is useful when you want to use a customized `.env` file for the project. In this case, manually create the project directory and then, inside the directory, create the  `.env` file and run `generate-project generate .`.

### Publishing Setup

The `--secrets` and `--local-env` options enable automated and manual publishing workflows. They require an `.env` file with the following tokens:

```bash
# .env file
TEST_PYPI_TOKEN=pypi-...      # Token for TestPyPI publishing
PYPI_TOKEN=pypi-...           # Token for PyPI publishing  
RTD_TOKEN=rtd_...             # Token for ReadTheDocs publishing
```

#### Token Location

The `.env` file should be located in one of the following locations (searched in order):

1. Path specified by `--env` option
2. Current working directory
3. Parent directories (searched upward)
4. If no .env file is found, the application falls back to reading the tokens from environment variables.

#### Publishing Options Explained

**GitHub Secrets (`--secrets`)**:   
Creates GitHub epository secrets from `.env` tokens, enabling automated publishing to PyPI and RTD through CI/CD workflows. Requires GitHub CLI authentication.

**Local .env (`--local-env`)**:   
Creates a project-specific `.env` file in the project directory to be used by manual publishing tasks. This is useful to freeze the publishing credentials of the project.


## config Command

Configure default values for project configuration parameters. These defaults will be used automatically in future `generate` commands.

### Synopsis

```bash
generate-project config [OPTIONS]
```

### Options

The `config` command accepts the same project configuration options as the `generate` command:

| Option | Description |
|--------|-------------|
| `--author_name` | Set default author name |
| `--email` | Set default email address |
| `--github_username` | Set default GitHub username |
| `--version` | Set default initial version |
| `--description` | Set default project description |
| `--python_min_version` | Set default minimum Python version |
| `--manager` | Set default package manager (`poetry` or `uv`) |
| `--autodoc_mock_imports` | Set default autodoc mock imports |
| `--complex_mock_modules` | Set default complex mock modules |
| `--google_analytics_id` | Set default Google Analytics ID |

### Configuration File

The configuration is stored in `/templates/config.yaml` within the folder where the application is installed and follows this format:

```yaml
default_context:
  author_name: Your Name
  email: your.email@example.com
  github_username: yourusername
  version: 0.0.0
  # ... other defaults
```

### Examples

#### Set Personal Defaults

```bash
generate-project config \
    --author_name="John Doe" \
    --email="john@example.com" \
    --github_username="johndoe" \
```

#### Update Project Defaults

```bash
generate-project config \
    --description="My project" \
    --python_min_version="3.10" \
    --version="0.0.0"
```

After setting defaults, you can omit these parameters in future `generate` commands.

## install-skills Command

Install the Claude Code assets bundled with generate-project into a `.claude` directory. These
assets are a set of slash commands (and one skill) that automate common maintenance tasks:

| Asset | Type | What it does |
|-------|------|--------------|
| `/release-docs` (+ `release-docs` skill) | command + skill | Drafts the four `.tmp_release_docs/` release artifacts from the diff since the last release tag |
| `/update-dev-env` | command | Syncs a generated repo's dev-environment files (`Makefile`, `run.sh`, workflows, …) with a released template version, preserving your customizations |
| `/migrate-poetry-to-uv` | command | Migrates a Poetry-based generated repo to UV: converts `pyproject.toml`, swaps the lockfile, and re-syncs infra files from the UV template |

### Synopsis

```bash
generate-project install-skills [OPTIONS]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--dest` | Target `.claude` directory to install into | `~/.claude` |
| `--force` | Overwrite existing files | Keep existing files |
| `--dry-run` | Show what would be installed without writing | — |

### Where the assets can be installed

There are three ways to install the bundled assets, depending on where you want them:

| Command | Installs into | Use when |
|---------|---------------|----------|
| `generate-project install-skills` | `~/.claude` (global) | You want the commands available in every repository |
| `generate-project generate <name> --install-skills` | the new project's `.claude/` | You want them bound to a project as you create it |
| `python scripts/install_claude_skills.py` (in a generated repo) | the repo's `.claude/` | A collaborator cloned the repo and wants them locally |

The in-repo `scripts/install_claude_skills.py` copies from an installed `generate_project` when
available and otherwise asks before downloading the files from GitHub (`--yes` to skip the prompt,
`--ref` to pick a version). All three read the same auto-generated asset manifest, so they install
an identical set of files.

### Codex bootstrap skill

The Claude asset bundle also includes a `generate-codex-assets` bootstrap skill for Codex users.
It does not change the Claude install flow. Instead, it generates Codex skills, and optionally
Codex prompt wrappers, from the same `asset_manifest.txt` inventory used by the Claude installers.

From a `generate-project` checkout:

```bash
mkdir -p ~/.agents/skills
cp -R src/generate_project/claude_assets/skills/generate-codex-assets ~/.agents/skills/
```

From a repository generated by `generate-project`, first install or download the bundled Claude
assets, then copy the bootstrap skill into Codex's skill folder:

```bash
python scripts/install_claude_skills.py --yes
mkdir -p ~/.agents/skills
cp -R .claude/skills/generate-codex-assets ~/.agents/skills/
```

Then start or restart Codex and invoke `$generate-codex-assets`. The helper script resolves source
assets from a local checkout, an installed `generate_project` package, or GitHub (`--yes --ref
<ref>` for non-interactive GitHub downloads). By default it writes Codex skills to `.agents/skills`;
pass `--skill-dest ~/.agents/skills` for global skills and `--prompts --prompt-dest
~/.codex/prompts` to also create slash-command-like prompt wrappers from manifest-listed command
files.

### Examples

```bash
generate-project install-skills                    # Install globally into ~/.claude
generate-project install-skills --dry-run          # Preview without writing anything
generate-project install-skills --force            # Overwrite existing files
generate-project install-skills --dest ./.claude   # Install into a specific .claude directory
```

## Generated Project Structure

The `generate` command creates a complete Python project with the following structure:

```
project-name/
├── .github/workflows/         # GitHub actions for CI/CD
│   ├── docs.yml               # Documentation building and testing
│   ├── tests.yml              # Code quality and testing
│   ├── release.yml            # Automated releases and publishing
│   └── update_rtd.yml         # Manual ReadTheDocs updates
├── .vscode/                   # VS Code configuration
│   ├── settings.json          # Editor settings, linting, formatting
│   ├── launch.json            # Debug configurations
│   └── tasks.json             # Task definitions
├── docs/                      # Sphinx documentation
│   ├── api/                   # Auto-generated API docs
│   ├── guides/                # User guides
│   ├── conf.py                # Sphinx configuration
│   └── index.md               # Documentation home
├── src/package_name/          # Source code
│   └── __init__.py            # Package initialization
├── tests/                     # Test directory
├── examples/                  # Example usage (libraries only; removed for applications)
├── scripts/                   # Release management scripts
├── .env                       # Environment variables (if --local-env used)
├── .gitignore                 # Git ignore rules
├── .readthedocs.yaml          # ReadTheDocs configuration
├── CLAUDE.md                  # Claude Code integration guide
├── CredentialManagement.md    # Token management documentation
├── LICENSE                    # MIT License
├── Makefile                   # Development commands
├── pyproject.toml             # Project configuration
├── run.sh                     # Development task runner
└── README.md                  # Project documentation
```

## Integration with Development Workflow

The generated projects include comprehensive development tooling:

### Code Quality Tools
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting and style checking
- **mypy**: Static type checking
- **pylint**: Advanced linting and code analysis

### Testing Framework
- **pytest**: Test runner with plugin support
- **pytest-cov**: Coverage reporting

### Documentation System
- **Sphinx**: Documentation generation
- **MyST-Parser**: Markdown support in Sphinx
- **autodoc**: Automatic API documentation from docstrings
- **ReadTheDocs**: Automated documentation hosting

### CI/CD Workflows
- **Tests**: Run on pull requests and pushes
- **Docs**: Build and validate documentation
- **Release**: Automated PyPI publishing on new version (using git tags)
- **RTD Update**: Manual documentation updates

# Development Workflow

The generated project includes a Makefile with common development tasks:

```bash

# Environment Setup
make venv                 # Create and activate a local virtual environment
make install              # Install core dependencies
make install-dev          # Install all development dependencies

# Code quality
make format               # Run code formatters
make lint                 # Run linters
make check                # Run format + lint + tests on all files
make pre-commit           # Run format and lint only on changed files, then tests

# Testing
make test                 # Run tests
make test-cov             # Run tests with coverage
make coverage             # Generate coverage report

# Documentation
make docs-api             # Generate API documentation
make docs                 # Build documentation
make docs-live            # Start live preview server

# Run
make run                  # Run the application, or an example of the library

# Worktree lifecycle (Supacode, requires --supacode)
make worktree-setup       # Prepare a freshly created worktree
make worktree-archive     # Tear down a worktree before archiving
make worktree-delete      # Guardrail + teardown before deleting

# Release tasks will bump the version, create a new release and publish it
make release-major        # Create major release
make release-minor        # Create minor release
make release-micro        # Create micro (patch) release
make release-rc           # Create release candidate
make release-beta         # Create beta pre-release
make release-alpha        # Create alpha pre-release
```

Run `make help` for a complete list of the development tasks available.

### Release Artifacts and Drafts

Each release task bumps the version, updates `CHANGELOG.md`, and writes and commits a
`RELEASE_NOTES.md` before creating the release commit and tag. The release workflow
(`release.yml`) uses `RELEASE_NOTES.md` as the GitHub Release body when it was part of the
tagged commit; otherwise it extracts that version's entry from `CHANGELOG.md`.

By default the commit message, tag message, changelog entry and release notes are generated
automatically and opened in your editor for review. You can instead pre-draft any of them in a
`.tmp_release_docs/` folder:

| Draft file | Overrides |
|------------|-----------|
| `commit.txt` | Release commit message |
| `tag.txt` | Annotated tag message |
| `changelog.md` | `CHANGELOG.md` entry |
| `release_notes.md` | `RELEASE_NOTES.md` body |

A draft is used only when it exists, is non-empty, and was modified more recently than the
previous release tag; otherwise you are prompted to continue with the generated content (each
draft is confirmed independently). The folder is git-ignored. The older `--changes` flag is
deprecated in favor of these drafts.

#### The release-docs Claude skill

A companion **`release-docs`** Claude Code skill (and `/release-docs` command) drafts the four
`.tmp_release_docs/` files from the diff since the previous release tag, so you can review and
tweak them instead of writing each artifact by hand. It ships bundled with generate-project
alongside the `/update-dev-env` and `/migrate-poetry-to-uv` commands — install any of them with
the [`install-skills` command](#install-skills-command) (globally, into a new project via
`generate --install-skills`, or into an existing repo via `scripts/install_claude_skills.py`).
Codex users can install the bundled `generate-codex-assets` bootstrap skill described in the
install-skills section to generate Codex skills and optional prompt wrappers from the same
manifest-listed files.

# Error Handling

### Common Issues

#### Missing Authentication Secrets
```
Error: Cannot create GitHub secrets or .env file.
The following environment variables are missing:
```

**Solution**: Make sure that the authentication tokens (`TEST_PYPI_TOKEN`, `PYPI_TOKEN` and `RTD_TOKEN`) are available on a `.env` file or as environment variables.

#### GitHub CLI Not Installed
```
Error: GitHub CLI (gh) not installed.
Install it from: https://cli.github.com/
```

**Solution**: Install the GitHub CLI from [https://cli.github.com/](https://cli.github.com/)

#### GitHub CLI Not Authenticated
```
Error: GitHub CLI not authenticated.
Run: gh auth login
```

**Solution**: Authenticate with GitHub CLI using `gh auth login` and follow the prompts.

#### Project Directory Already Exists
```
Error: Directory <project-name> already exists.
```

**Solution**: Either use a different project name, remove the existing directory, or use `.` to generate the project inside an existing directory.

#### Project File Already Exists
```
Error: Cannot generate into existing directory, conflicting files: <file1>, <file2>, ...
```

**Solution**: When using `.` as the project name, make sure that the current directory does not contain any files or subdirectories that collide with the project template structure.
