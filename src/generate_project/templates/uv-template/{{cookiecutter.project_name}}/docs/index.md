# {{ cookiecutter.project_name }}

{{ cookiecutter.description }}

## Overview

{% if cookiecutter.project_type == "application" -%}
This documentation covers the {{ cookiecutter.project_name }} application.
{%- else -%}
This documentation covers the {{ cookiecutter.project_name }} library.
{%- endif %}

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
{{ cookiecutter.project_name }}
```

Or run as a module:

```bash
python -m {{ cookiecutter.package_name }}
```

{% endif %}
## Quick Start

{% if cookiecutter.project_type == "application" -%}
```bash
pip install {{ cookiecutter.project_name }}

{{ cookiecutter.project_name }}
```
{%- else -%}
```python
from {{ cookiecutter.package_name }} import Example

# Initialize
example = Example()

# Use the library
result = example.run()
print(result)
```
{%- endif %}

```{toctree}
:hidden:
:maxdepth: 2
:caption: Contents

Home <self>
Guides <guides/index>
API Reference <api/index>
```

```{toctree}
:hidden:
:maxdepth: 1
:caption: Useful Links

GitHub Repository <https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}>
PyPI Package <https://pypi.org/project/{{ cookiecutter.project_name }}/>
Issue Tracker <https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}/issues>
```
