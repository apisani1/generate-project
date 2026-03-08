# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses UV for dependency management and a custom `run.sh` script for development tasks. All commands can be executed via either the Makefile (which delegates to `run.sh`) or directly via `run.sh`.

### Environment Setup
```bash
make venv                 # Create and activate local virtual environment
make install              # Install core dependencies
make install-lint         # Install linting dependencies
make install-test         # Install testing dependencies
make install-docs         # Install documentation dependencies
make install-dev          # Install all development dependencies (dev, test, lint, typing and docs dependency groups)
./run.sh install:all      # CI alternative: install all dependencies without interaction
```

### Code Quality
```bash
make format               # Format code with black and isort
make format-diff          # Run formatters on changed files
make lint                 # Run mypy, flake8, and pylint
make lint-diff            # Run all linters on changed files
make check                # Run format + lint + tests on all files(local development)
make pre-commit           # Format and lint only on changed files
./run.sh check:ci         # CI version (format only checks, no file modifications)

```

### Testing
```bash
make test                 # Run all tests
make test-cov             # Run tests with coverage
make coverage             # Generate coverage report
make test-verbose         # Run tests with verbose output
./run.sh tests:pattern "test_name"  # Run only tests matching pattern
```

### Documentation
```bash
make docs-api             # Generate API documentation automatically
make docs                 # Build Sphinx documentation
make docs-live            # Start live documentation server with auto-reload
make docs-clean           # Clean and rebuild documentation
```

### Package Building
```bash
make build                # Build package with UV
make validate-build       # Validate package builds correctly
make clean                # Clean build artifacts
```

## Project Architecture

This is a Python project generator tool that creates well-structured Python projects using cookiecutter templates.

### Core Components

**Main Application** (`src/generate_project/main.py`):
- CLI application with two main commands: `generate` and `config`
- Handles project generation via cookiecutter templates
- Integrates with GitHub CLI for repository creation
- Manages environment variables and configuration files
- Supports automated secret creation and publishing setup

**Template System** (`src/generate_project/templates/`):
- `poetry-template/`: Cookiecutter template for Poetry-based Python projects
- `uv-template/`: Cookiecutter template for UV-based Python projects (hatchling build backend)
- `cookiecutter.json`: Template configuration with project parameters (shared schema)
- `config.yaml`: User-specific default values for template parameters

**Configuration Management**:
- Global config: `cookiecutter.json` defines all available template parameters
- User config: `config.yaml` stores user-specific defaults (can be updated via `config` command)
- Environment variables: `.env` file support for tokens (PyPI, GitHub, ReadTheDocs)

### Key Features

1. **Project Generation**: Creates complete Python project structure with UV or Poetry, testing, linting, documentation, and CI/CD
5. **Package Manager Selection**: Choose between UV (default) and Poetry via `--manager` flag
2. **GitHub Integration**: Optional GitHub repository creation with automated secret setup
3. **Publishing Setup**: Automated PyPI token configuration for both local and CI/CD publishing
4. **Template Customization**: Flexible cookiecutter-based templating system

### Development Workflow

The project uses UV for dependency management with multiple dependency groups:
- `test`: pytest and testing utilities
- `lint`: black, isort, flake8, pylint, mypy
- `docs`: Sphinx and documentation tools
- `typing`: mypy type checking

Code formatting follows Black style with 119 character line length. All tools are configured in `pyproject.toml`.

### Testing Strategy

Tests are located in `tests/` and use pytest with the following specialized test modules:
- `test_bake.py`: Tests Poetry cookiecutter template generation
- `test_uv_bake.py`: Tests UV cookiecutter template generation
- `test_dependencies.py`: Validates dependency management
- `test_structure.py`: Verifies generated project structure
- `test_docs.py`: Tests documentation generation
- `test_github.py`: Tests GitHub integration features

The project excludes cookiecutter template files from linting and type checking to avoid conflicts with template syntax.

See @./notes for additional private information

