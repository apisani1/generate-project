# New Python Project 
A Python project template based on Poetry for package management. This template provides everything you need to get started with a well-structured Python project, including documentation, testing, linting, and GitHub CI integration.

## Features

📦 Poetry for dependency management and packaging   
📚 Sphinx Documentation with auto-generated API docs and live preview   
✅ Testing Framework with pytest and test coverage reports   
🧹 Code Quality Tools including flake8, mypy, pylint, and isort   
🔄 GitHub Actions for CI/CD workflows for tests and documentation   
📝 ReadTheDocs Integration for hosting documentation   
📋 Project Structure following best practices   
🚀 Automated Release Process for versioning and publishing   

## Requirements

Python 3.10+   
Cookiecutter 2.6.0+     
Poetry 2.1.1+   

## Usage

### Basic Usage

```bash
cookiecutter https://github.com/apisani1/poetry-project-template.git
```

This will prompt you for configuration values and create a new project based on the template.

### Advanced Usage

You can also provide configuration values directly:
```bash
cookiecutter https://github.com/apisani1/poetry-project-template.git \
--no-input \
project_name="My-Amazing-Project" \
author_name="Your Name" \
email="your.email@example.com" \
github_username="yourusername" \
python_version="3.11"
```

## Project Structure

The generated project will have the following structure:

```
your-project/
├── .github/                # GitHub Actions workflows
│   ├── workflows/
│   │   ├── docs.yml        # Documentation build and checks
│   │   └── release.yml     # Release automation
├── docs/                   # Sphinx documentation
│   ├── api/                # Auto-generated API docs
│   ├── guides/             # How-to guides
│   ├── conf.py             # Sphinx configuration
│   ├── index.md            # Documentation home page
│   └── Makefile            # Documentation build tool
├── src/                    # Source code
│   └── your_package/       # Your package name
│       └── init.py         # Package initialization
├── tests/                  # Test suite
│   └── init.py
├── .gitignore              # Git ignore rules
├── .readthedocs.yaml       # ReadTheDocs configuration
├── LICENSE                 # MIT License
├── Makefile                # Development tasks
├── pyproject.toml          # Project configuration & dependencies
└── README.md               # Project readme
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `project_name` | `my_project` | Name of the project |
| `package_name` | Based on project_name | Python package name (importable) |
| `author_name` | `Antonio Pisani` | Author's name |
| `email` | `antonio.pisani@gmail.com` | Author's email |
| `github_username` | `apisani1` | GitHub username |
| `version` | `0.1.0` | Initial version number |
| `description` | `A short description of the project` | Short project description |
| `python_version` | `3.10` | Python version requirement |

## GitHub Repository Setup

The following repository secrets ared needed for the GitHub workflows: 

```
TEST_PYPI_TOKEN
PYPI_TOKEN
RTD_TOKEN
```

## Development Workflow

The generated project includes a Makefile with common development tasks:

```bash

# Install dependencies
make install              # Install main dependencies
make install-dev          # Install all development dependencies

# Code quality
make format               # Run code formatters
make lint                 # Run linters

# Testing
make test                 # Run tests
make test-cov             # Run tests with coverage

# Documentation
make docs                 # Build documentation
make docs-live            # Start live preview server
make docs-api             # Generate API docs

# Releasing
make build                # Build package
make publish              # Publish to PyPI
```

## Customization
You can customize this template by:

1. Forking the repository   
2. Modifying files in the template structure   
3. Updating cookiecutter.json with your preferred defaults 

## License
This project template is released under the MIT License. See the LICENSE file for details.
