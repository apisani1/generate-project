docs_files = [
    "docs",
    "docs/api",
    "docs/guides",
    "docs/conf.py",
    "docs/Makefile",
]

github_workflow_files = [
    ".github/workflows/docs.yml",
    ".github/workflows/release.yml",
    ".github/workflows/tests.yml",
    ".github/workflows/update_rtd.yml",
]

vscode_files = [
    ".vscode/settings.json",
    ".vscode/launch.json",
    ".vscode/tasks.json",
]

expected_files = (
    [
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "Makefile",
        ".gitignore",
        ".readthedocs.yaml",
        "tests/__init__.py",
    ]
    + vscode_files
    + docs_files
    + github_workflow_files
)

custom_context = {
    "project_name": "test-project",
    "author_name": "Test User",
    "email": "test@example.com",
    "github_username": "testuser",
    "version": "0.2.0",
    "description": "A test project created for testing purposes",
    "python_min_version": "3.11",
}

library_context = {
    "project_name": "test-library",
    "author_name": "Test User",
    "email": "test@example.com",
    "github_username": "testuser",
    "version": "0.1.0",
    "description": "A test library project",
    "python_min_version": "3.11",
    "project_type": "library",
}

application_context = {
    "project_name": "test-application",
    "author_name": "Test User",
    "email": "test@example.com",
    "github_username": "testuser",
    "version": "0.1.0",
    "description": "A test application project",
    "python_min_version": "3.11",
    "project_type": "application",
}

# UV template contexts
uv_custom_context = {
    "project_name": "test-uv-project",
    "author_name": "Test User",
    "email": "test@example.com",
    "github_username": "testuser",
    "version": "0.2.0",
    "description": "A test UV project created for testing purposes",
    "python_min_version": "3.11",
}

uv_library_context = {
    "project_name": "test-uv-library",
    "author_name": "Test User",
    "email": "test@example.com",
    "github_username": "testuser",
    "version": "0.1.0",
    "description": "A test UV library project",
    "python_min_version": "3.11",
    "project_type": "library",
}

uv_application_context = {
    "project_name": "test-uv-application",
    "author_name": "Test User",
    "email": "test@example.com",
    "github_username": "testuser",
    "version": "0.1.0",
    "description": "A test UV application project",
    "python_min_version": "3.11",
    "project_type": "application",
}
