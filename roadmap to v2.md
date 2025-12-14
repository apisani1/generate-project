# Update generate-project to launch v2.0.0

This document describes the steps we will implement to launch v2.0.0 of this project.

This future release main additional functionaly will be offer the option to use UV or Poetry as package and dependency manager and migrate the project itself to UV.

This is the secuence of planned releases:

- v1.0.3 Update project scripts, workflows and tools
- v1.1.0 Update cookiecutter Poetry template
- v1.2.0 Add option to create a project for a library or an applcation
- v1.3.0 Add cookiecuter UV template and option to choose between UV and poetry
- V2.0.0 Migrate the project itself from Poetry to UV

## v1.03 Update project scripts, workflows and tools

Using this repo as a reference:

/Users/antonio/AI/MyCode/mcp-multi-server

Update the following files:

.github/workflows/delete_workflows_runs.yml (new)   
.github/workflows/docs.yml     
.github/workflows/release.yml    
.github/workflows/update_rtd.yml   
.gitignore   
.pypirc   
.readthedocs.yaml   
.vscode/launch.json   
.vscode/settings.json    
.vscode/task.json   
Makefile (note that mcp-multi-server is a library and generate-project is an app)   
pyproject.toml (note that mcp-multi-server is a library and generate-project is an app)   
run.sh (note that mcp-multi-server is a library and generate-project is an app)   
scripts/release.py   
scripts/reset_version.py   
scripts/update_versions.py  

**Ask me for clarification if you don't undertand the required updates on an specific file or if you think that there is a better way to do it**

## v1.1.0 Update cookiecutter Poetry template

Using the most recent version on this files:

.github/workflows/delete_workflows_runs.yml (new)   
.github/workflows/docs.yml     
.github/workflows/release.yml    
.github/workflows/update_rtd.yml   
.gitignore   
.pypirc   
.readthedocs.yaml   
.vscode/launch.json   
.vscode/settings.json    
.vscode/task.json   
Makefile      
pyproject.toml     
run.sh   
scripts/release.py   
scripts/reset_version.py   
scripts/update_versions.py   

update the corresponding files in:

scr/generate_project/templates/poetry-template/{{cookiecutter.project_name}}

remember that you are update a cookicuter template and by mindfull of the jinja2 syntax for the project being generated and specially the scaping used in the github workflows.

**Ask me for clarification if you don't undertand the required updates on an specific file or if you think that there is a better way to do it**

## v1.2.0 Add option to create a project for a library or an application

add an option named --library to the command "generate-project generate" that customize the project files for a library building project.

by defualt generate-project generate will generate project files for a application building project.

# v1.3.0 Add cookiecuter UV template and option to choose between UV and poetry

Based on the poetry template located at src/generate-project/templates/poetry-template create a folder named uv-template and mirror all files but migrating poetry commands and configurations to uv.

Then add a new option named --manager to the command "generate-project generate" that allows to use the package manager:

--manager poetry for Poetry
--manager uv for UV

by default UV will be the package and project manager

## V2.0.0 Migrate the project itself from Poetry to UV

We will migrate the following files:

.github/workflows/delete_workflows_runs.yml (new)   
.github/workflows/docs.yml     
.github/workflows/release.yml    
.github/workflows/update_rtd.yml   
.gitignore   
.pypirc   
.readthedocs.yaml   
.vscode/launch.json   
.vscode/settings.json    
.vscode/task.json   
Makefile      
pyproject.toml     
run.sh   
scripts/release.py   
scripts/reset_version.py   
scripts/update_versions.py  

of this repo to use UV instead of Poetry
