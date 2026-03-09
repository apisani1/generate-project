# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses a combination of Poetry for dependency management and a custom `run.sh` script for development tasks. All commands can be executed via either the Makefile (which delegates to `run.sh`) or directly via `run.sh`.

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
make build                # Build package with Poetry
make validate-build       # Validate package builds correctly
make clean                # Clean build artifacts
```

## Development Workflow

The project uses Poetry for dependency management with multiple optional dependency groups:
- `test`: pytest and testing utilities
- `lint`: black, isort, flake8, pylint, mypy
- `docs`: Sphinx and documentation tools
- `typing`: mypy type checking

Use `poetry add <pkg>` to add dependencies and `poetry install` to install from lockfile. Avoid using `pip install` directly.

## Code Style

- Formatter: Black with 119 character line length
- Import sorting: isort (configured to be Black-compatible)
- Linting: flake8 + pylint + mypy (all configured in `pyproject.toml`)
- Do not add inline `# noqa` without a specific reason

## Project Structure

<!-- FILL IN: Describe what this project does and its key directories/files. Example:
- `src/{{ cookiecutter.package_name }}/main.py`: CLI entry point
- `src/{{ cookiecutter.package_name }}/core.py`: Core business logic
- `tests/`: pytest tests mirroring src structure
-->

## Gotchas

<!-- FILL IN: Add project-specific gotchas as you discover them.
     Tip: Press `#` during a Claude Code session to auto-incorporate session learnings here. -->

See @./notes for additional private information
