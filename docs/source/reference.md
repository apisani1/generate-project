# Reference

This is the comprehensive reference guide for generate-project, covering all commands, options, and configuration parameters.

## Commands Overview

generate-project provides two main commands:

- **generate**: Create a new Python project from templates
- **config**: Configure default project parameters

## generate Command

Create a new Python project from cookiecutter templates with comprehensive development setup.

### Synopsis

```bash
generate-project generate PROJECT_NAME [OPTIONS]
```

### Arguments

#### Required Arguments

| Argument | Description |
|----------|-------------|
| `PROJECT_NAME` | Name of the project to create (positional argument) |

#### Project Configuration Options

These options configure the project metadata and can be saved as defaults using the `config` command:

| Option | Description |
|--------|-------------|
| `--author_name` | Author's full name |
| `--email` | Author's email address |
| `--github_username` | GitHub username for repository creation |
| `--version` | Initial project version number |
| `--description` | Short project description |
| `--python_version` | Python version requirement |
| `--package_name` | Python package name (can be auto-generated from project name) |
| `--autodoc_mock_imports` | Comma-separated list of modules to mock for Sphinx autodoc |
| `--complex_mock_modules` | Comma-separated list of complex modules requiring special mocking |
| `--google_analytics_id` | Google Analytics tracking ID for documentation SEO metrics |

#### Behavior Control Options

| Option | Description | Default |
|--------|-------------|---------|
| `--no-install` | Skip installing dependencies with Poetry | Install dependencies |
| `--no-git` | Skip Git repository initialization | Initialize Git repository |

#### GitHub Integration Options (requires gh CLI)

| Option | Description | Default |
|--------|-------------|---------|
| `--github` | Create a private GitHub repository  | No repository creation |
| `--public` | Create a public GitHub repository | Private repository |
| `--secrets` | Create GitHub repository secrets for PyPl and RTD integration | No secrets creation |

#### Publishing Setup Options

| Option | Description | Default |
|--------|-------------|---------|
| `--pypirc` | Create .pypirc file with PyPl tokens for local publishing | No .pypirc creation |

#### File Path Options

| Option | Description | Default |
|--------|-------------|---------|
| `--env` | Path to .env file containing tokens for repository secrets | `.env` (location auto-detected) |
| `--template` | Path to custom cookiecutter template | Built-in poetry template |

### Examples

#### Basic Project Creation

```bash
generate-project generate my-awesome-project
```

#### Custom Project with Metadata

```bash
generate-project generate my-project \
    --author_name="John Doe" \
    --email="john@example.com" \
    --github_username="johndoe" \
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
    --pypirc
```

#### Using Custom Template

```bash
generate-project generate my-project \
    --template="/path/to/custom/template" \
    --author_name="John Doe"
```

### Publishing Setup

The `--secrets` and `--pypirc` options enable automated and manual publishing workflows. They require an `.env` file with the following tokens:

```bash
# .env file
TEST_PYPI_TOKEN=pypi-...      # Token for TestPyPI publishing
PYPI_TOKEN=pypi-...           # Token for PyPI publishing  
RTD_TOKEN=rtd_...             # Token for ReadTheDocs publishing
```

The .env file should be located in the folder where generate-project is executed or increasingly higher folders.

#### GitHub Secrets (--secrets)
Creates repository secrets from .env tokens, enabling automated publishing to PyPl and RTD through GitHub Actions.

#### Local .pypirc (--pypirc)
Creates a `.pypirc` file for manual publishing using `make publish:test` and `make publish`.

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
| `--python_version` | Set default Python version requirement |
| `--autodoc_mock_imports` | Set default autodoc mock imports |
| `--complex_mock_modules` | Set default complex mock modules |
| `--google_analytics_id` | Set default Google Analytics ID |

### Configuration File

The configuration is stored in `src/generate_project/templates/config.yaml` and follows this format:

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
    --version="0.0.0"
```

#### Update Specific Defaults

```bash
generate-project config \
    --description="My project" \
    --python_version="ˆ3.10"
```

After setting defaults, you can omit these parameters in future `generate` commands:

```bash
# Uses configured defaults for author_name, email, etc.
generate-project generate new-project
```

## Requirements

- Python 3.10+
- Cookiecutter 2.6.0+
- PyYAML 6.0.0+
- python-dotenv 1.1.0+

### Optional Requirements

- **GitHub CLI (gh)**: Required for `--github`, `--public` and `--secrets` options
- **VS Code**: Used by the release script for editing release commit messages and changelogs

## Generated Project Structure

The `generate` command creates a complete Python project with the following structure:

```
project-name/
├── .github/workflows/         # GitHub Actions CI/CD
│   ├── docs.yml               # Documentation building
│   ├── tests.yml              # Code quality and testing
│   ├── release.yml            # Automated releases
│   └── update_rtd.yml         # ReadTheDocs updates
├── docs/                      # Sphinx documentation
│   ├── api/                   # Auto-generated API docs
│   ├── guides/                # User guides
│   ├── conf.py                # Sphinx configuration
│   └── index.md               # Documentation home
├── src/package_name/          # Source code
│   └── __init__.py            # Package initialization
├── tests/                     # Test suite
├── scripts/                   # Development scripts
├── .gitignore                 # Git ignore rules
├── .readthedocs.yaml          # ReadTheDocs configuration
├── LICENSE                    # MIT License
├── Makefile                   # Development commands
├── pyproject.toml             # Project configuration
├── run.sh                     # Development task runner
└── README.md                  # Project documentation
```

## Error Handling

### Common Issues

#### GitHub CLI Not Authenticated
```
Error: GitHub CLI not authenticated.
Run: gh auth login
```

#### Missing .env File
```
Error: Cannot create secrets/pypirc without environment file
Expected location: ./.env
```

#### Invalid Project Name
Project names should follow Python package naming conventions and avoid reserved keywords.

### Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error (invalid arguments, missing dependencies, etc.) |

## Integration with Development Workflow

The generated projects include comprehensive development tooling:

- **Code Quality**: Black, isort, flake8, mypy, pylint
- **Testing**: pytest with coverage reporting
- **Documentation**: Sphinx with auto-generated API docs
- **CI/CD**: GitHub Actions workflows
- **Publishing**: Automated PyPI releases
- **Documentation**: Automated RTD publishing
- **Development**: Make targets and shell scripts for common tasks

Use `make help` in any generated project to see available development commands.
