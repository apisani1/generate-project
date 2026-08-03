# {{ cookiecutter.project_name }}

{{ cookiecutter.description }}

## Overview
{% if cookiecutter.project_type == "application" %}
This documentation covers the {{ cookiecutter.project_name }} application.
{% else %}
This documentation covers the {{ cookiecutter.project_name }} library.
{% endif %}
## Installation

```bash
pip install {{ cookiecutter.project_name }}
```

Or, if you use Poetry:

```bash
poetry add {{ cookiecutter.project_name }}
```
{% if cookiecutter.project_type == "application" %}
## Usage

Run the application:

```bash
{{ cookiecutter.package_name }}
```

Or run as a module:

```bash
python -m {{ cookiecutter.package_name }}
```
{% endif %}
## Quick Start
{% if cookiecutter.project_type == "application" %}
```bash
pip install {{ cookiecutter.project_name }}

{{ cookiecutter.package_name }}
```
{% else %}
```python
from {{ cookiecutter.package_name }} import Example

# Initialize
example = Example()

# Use the library
result = example.run()
print(result)
```
{% endif %}
## Development

```bash
make install-dev          # Install all development dependencies
make run                  # Run the {% if cookiecutter.project_type == "application" %}application{% else %}example in examples/main.py{% endif %}
make run ARGS="--help"    # Run with arguments
make pre-commit           # Format and lint changed files
make test                 # Run the test suite
make help                 # List every available target
```

To change how `make run` starts this project, create an executable `scripts/run.sh`; it takes
precedence over the built-in defaults and is not overwritten by dev-environment syncs.

### Git worktrees

```bash
make worktree-setup       # Prepare a freshly created worktree
make worktree-archive     # Tear down a worktree before archiving
make worktree-delete      # Guardrail + teardown before deleting a worktree
```

`make worktree-delete` refuses to run when the worktree has uncommitted changes, commits that
exist on no other ref, or stashes on its branch — override with `SUPACODE_FORCE_DELETE=1`. Add
project-specific teardown in an executable `scripts/worktree-archive.sh` (or `-setup`/`-delete`).

