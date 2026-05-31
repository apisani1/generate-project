[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/generate-project.svg?v=2.0.0.post1)](https://pypi.org/project/generate-project/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Documentation Status](https://readthedocs.org/projects/generate-project/badge/?version=latest)](https://generate-project.readthedocs.io/en/latest/?badge=latest)

# Generate Project 
A Python project folder generator with support for **UV** and **Poetry** package managers. The generated folder provides everything you need to get started with a well-structured Python project, including development tasks for formatting, linting, documentation, testing, and CI/CD.

## Features

📦 UV or Poetry for dependency management and packaging   
🧹 Code quality tools including  black, isort, flake8, mypy and pylint        
📚 Sphinx based documentation with auto-generated API docs and live preview   
✅ Testing framework with pytest and test coverage reports   
🔄 GitHub actions with CI/CD workflows for tests, documentation and release management   
🐍 PyPl package publishing automation with version control   
📝 ReadTheDocs integration for hosting documentation   
🚀 Automated release process for versioning and publishing   
📋 Project structure following best practices   
  

## Requirements

Python 3.10+   
Cookiecutter 2.6.0+  
PyYAML 6.0.0+    
python-dotenv 1.1.0+   

## Installation

```bash
pip install generate-project
```

Or, if you use Poetry:

```bash
poetry add generate-project
```

Or, if you use UV:

```bash
uv add generate-project
```

## Quick Start

### Basic Usage

You can provide the project configuration values in the terminal command line:

```bash
generate-project generate "project-name" \
--author_name="Your Name" \
--email="your.email@example.com" \
--github_username="yourusername" \
--python_min_version="3.11"
...
```

### Project Configuration Options

These are the most important project configuration options:

| Option | Description |
|--------|-------------|
| `package_name` | Python package name (defaults to project_name)|
| `author_name` | Author's name |
| `email` | Author's email |
| `github_username` | GitHub username |
| `version` | Initial version number |
| `description` | Short project description |
| `python_min_version` | Minimum Python version |

### Advanced Usage

You can also save your own configuration values to be used as default values:
```bash
generate-project config \
--author_name="Your Name" \
--email="your.email@example.com" \
--github_username="yourusername" \
--python_min_version="3.11"
```

You can also set the default package manager:
```bash
generate-project config --manager uv
```

and then you can omit the saved configuration options:

```bash
generate-project generate "project-name"
...
```

## Package Manager

By default, generate-project creates projects using **UV**. Use the `--manager` flag to select **Poetry** instead:

| Manager | Build Backend | Dependency Format | Command |
|---------|--------------|-------------------|---------|
| UV (default) | hatchling | `[dependency-groups]` (PEP 735) | `--manager uv` |
| Poetry | poetry-core | `[tool.poetry.dependencies]` | `--manager poetry` |

```bash
# UV project (default)
generate-project generate my-project

# Poetry project
generate-project generate my-project --manager poetry
```

## Project Structure
The generated project will have the following structure:

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

  
## Project Types

By default, generate-project creates an **application** project with a CLI entry point. Use the `--library` flag to create a library project instead:

```bash
# Create an application (default)
generate-project generate my-app

# Create a library
generate-project generate my-lib --library
```

| Project Type | CLI Entry Point | main.py | Use Case |
|--------------|-----------------|---------|----------|
| Application | Yes | Yes | CLI tools, scripts |
| Library | No | No | Reusable packages, APIs |

## GitHub Repository Setup

The following options are available to setup a github repository for the project:

| Option | Description |   
|--------|-------------|   
| `--github` | Create a private github repository for the project |   
| `--public` | Create a public github repository for the project|    
| `--secrets` | Create repository secrets for the release management workflows |     

The following repository secrets can be automatically setup: 

`TEST_PYPI_TOKEN`   
`PYPI_TOKEN`   
`RTD_TOKEN`   

The tokens must be available in a .env file located in the directory where generate-project is executed or in any parent directory up the folder hierarchy. If no .env file is found, the application falls back to reading the tokens from environment variables.

## Development Workflow

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

Each release task bumps the version, updates `CHANGELOG.md`, writes and commits a
`RELEASE_NOTES.md` (used as the GitHub Release body), then creates the release commit and tag.
By default the commit message, tag message, changelog entry and release notes are generated for
you (and opened in your editor for review). To prepare them ahead of time, drop drafts in a
`.tmp_release_docs/` folder — `commit.txt`, `tag.txt`, `changelog.md`, `release_notes.md` — and
any draft present is used instead of the generated text. (The older `--changes` flag is
deprecated in favor of these drafts.)

Run `make help` for a complete list of the development tasks available.

## Acknowledgments

This project was inspired by the GitHub workflows and automation ideas
from [phitoduck/python-course-cookiecutter-v2](https://github.com/phitoduck/python-course-cookiecutter-v2).

While this project is an independent implementation and a full Python
application, the original repository provided valuable inspiration for
the CI/CD and automation approach.

We thank the original authors for their contributions and ideas.

## License
This project is released under the MIT License. See the LICENSE file for details.
