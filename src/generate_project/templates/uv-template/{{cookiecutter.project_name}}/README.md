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

Or, if you use UV:

```bash
uv add {{ cookiecutter.project_name }}
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
