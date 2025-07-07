# Generate Project 
A Python project folder generator based on Poetry for dependency and package management. The generated folder provides everything you need to get started with a well-structured Python project, including formatting, linting, documentation, testing, and CI/CD integration.

## Features

📦 Poetry for dependency management and packaging    
🧹 Code quality tools including  black, isort, flake8, mypy and pylint        
📚 Sphinx based documentation with auto-generated API docs and live preview   
✅ Testing framework with pytest and test coverage reports   
🔄 GitHub actions for CI/CD workflows for tests, documentation and release management   
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

## Quick Start

### Basic Usage

You can provide the project configuration values in the terminal command line:

```bash
generate-project generate "project-name" \
author_name="Your Name" \
email="your.email@example.com" \
github_username="yourusername" \
python_version="3.11"
...
```

### Project Configuration Options

These are the most important project configuration options:

| Option | Description |   
|--------|-------------|   
| `project_name` | Name of the project |   
| `package_name` | Python package name (importable) |   
| `author_name` | Author's name |   
| `email` | Author's email |   
| `github_username` | GitHub username |   
| `version` | Initial version number |   
| `description` | Short project description |   
| `python_version` | Python version requirement | 

### Advanced Usage

You can also save your configuration values to be used as default values:
```bash
generate-project config \
author_name="Your Name" \
email="your.email@example.com" \
github_username="yourusername" \
python_version="3.11"
```

and the you can omit the saved configuration options:

```bash
generate-project generate "project-name" 
...
```

## Project Structure
The generated project will have the following structure:

```
project-name/
├── .github/                # GitHub Actions workflows
│   ├── workflows/
│   │   ├── docs.yml        # Documentation build and checks
|   |   ├── tests.yml       # Code quality checks
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

  
## GitHub Repository Setup

The following options are available to setup a github repository for the project:

| Option | Description |   
|--------|-------------|   
| `--github` | Create a private github repository for the project |   
| `--public` | Create a public github repository for the project|    
| `--secrets` | Create repository secrets for the release management workflow |     

The following repository secrets can be automatically setup: 

`TEST_PYPI_TOKEN`   
`PYPI_TOKEN`   
`RTD_TOKEN`   

The tokens must be available in a .env file found in the folder where generate-project is executed or increasingly higher folders.

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
make release-minor        # Create a new release and bump the version
```

Run `make help` for a complete list of the make targets available.

## Customization
You can customize this template by:

1. Forking the repository   
2. Modifying files in the template structure base on cookiecutter 
3. Updating cookiecutter.json with your preferred defaults 

## License
This project template is released under the MIT License. See the LICENSE file for details.
