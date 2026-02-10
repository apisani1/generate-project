# Command Reference

This is the reference guide for generate-project, a command-line tool for generating Python project folders with pre-configured development tasks for formatting, linting, documentation, testing, release management and CI/CD.

## Commands Overview

generate-project provides two commands:

- **generate**: Create a new Python project folder with configurable parameters
- **config**: Configure default project parameters

For quick help use:
```bash
generate-project --help
generate-project --version
generate-project generate --help
generate-project config --help
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

#### Project Type Options

| Option | Description | Default |
|--------|-------------|---------|
| `--library` | Create a library project (no CLI entry point) | Application project |
| `--manager` | Package manager: `poetry` or `uv` | `poetry` |

When `--manager uv` is specified:
- Uses hatchling build backend instead of poetry-core
- Uses PEP 621 `[project]` metadata and `[dependency-groups]` (PEP 735)
- CI workflows use `astral-sh/setup-uv` instead of Poetry
- `run.sh` uses `uv sync`, `uv run`, `uv build`, `uv publish`

When `--library` is specified:
- No `[project.scripts]` section is added to `pyproject.toml`
- No `main.py` CLI entry point is created
- README focuses on API usage instead of CLI usage

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


# Release tasks will bump the version, create a new release and publish it
make release-major        # Create major release
make release-minor        # Create minor release
make release-micro        # Create micro (patch) release
make release-rc           # Create release candidate
make release-beta         # Create beta pre-release
make release-alpha        # Create alpha pre-release
```

Run `make help` for a complete list of the development tasks available.

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
Error: Cannot move <file name>, destination already exists.
```

**Solution**: When using `.` as the project name, make sure that the current directory does not contain any files or subdirectories that collide with the project template structure.
