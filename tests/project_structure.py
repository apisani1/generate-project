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
    "python_version": "3.11",
}
