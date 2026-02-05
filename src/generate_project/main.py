#!/usr/bin/env python3
"""
Python project generator using cookiecutter templates.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from enum import Enum
from pathlib import Path
from typing import (
    Dict,
    List,
    Optional,
)

import yaml
from dotenv import (
    find_dotenv,
    load_dotenv,
)
from generate_project import __version__  # noqa: F401


TOKEN_NAMES = ["TEST_PYPI_TOKEN", "PYPI_TOKEN", "RTD_TOKEN"]

PYPIRC_FILE_TEMPLATE = """[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = {pypi_token}

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = {test_pypi_token}
"""

ENV_FILE_TEMPLATE = """# Publishing tokens
TEST_PYPI_TOKEN={test_pypi_token}
PYPI_TOKEN={pypi_token}
RTD_TOKEN={rtd_token}
"""


class Colors(Enum):
    """ANSI color codes for terminal output."""

    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"  # No Color


def print_colored(message: str, color: Colors = Colors.NC) -> None:
    """Print message with color."""
    print(f"{color.value}{message}{Colors.NC.value}")


def run_command(
    cmd: List[str],
    cwd: Optional[Path] = None,
    check: bool = True,
    input: Optional[str] = None,
    extra_env: Optional[dict] = None,
) -> subprocess.CompletedProcess:
    """Run a command with error handling."""

    # Add any extra environment variables
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    try:
        return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True, input=input, env=env)
    except subprocess.CalledProcessError as e:
        print_colored(f"Command failed: {' '.join(cmd)}", Colors.RED)
        if e.stderr:
            print_colored(f"Error: {e.stderr}", Colors.RED)
        raise


def generate_project(
    project_name: str,
    template_path: Path,
    env_file: Path,
    install_deps: bool = True,
    init_git: bool = True,
    create_github: bool = False,
    create_public: bool = False,
    create_secrets: bool = False,
    create_pypirc: bool = False,
    create_local_env: bool = False,
    **kwargs: Optional[Dict],
) -> None:
    """Main project generation logic."""
    # Ensure template exists
    if not template_path.exists():
        print_colored(f"Error: Cookiecutter template not found at {template_path}", Colors.RED)
        sys.exit(1)

    # Ensure environment variables are loaded if needed
    if create_secrets or create_pypirc or create_local_env:
        if not load_dotenv(dotenv_path=env_file, override=True):
            print_colored(
                f"Warning: .env file not found at {env_file}, proceeding with existing environment variables",
                Colors.YELLOW,
            )
        missing_vars = missing_enviroment_secrets(TOKEN_NAMES)
        if len(missing_vars) > 0:
            print_colored("Error: Cannot create GitHub secrets, .pypirc file or .env file", Colors.RED)
            print_colored(f"The following environment variables are missing: {', '.join(missing_vars)}", Colors.RED)
            sys.exit(1)

    # Check if project directory already exists and handle "." case
    if project_name.strip() == ".":
        project_dir = Path.cwd()
        project_name = str(project_dir.name)
        create_project_dir = False
    else:
        project_dir = Path.cwd() / project_name
        if project_dir.exists():
            print_colored(f"Error: Directory '{project_name}' already exists.", Colors.RED)
            print_colored("Please choose a different project name or remove the existing directory:", Colors.RED)
            print_colored(f"  rm -rf {project_name}/", Colors.RED)
            sys.exit(1)
        create_project_dir = True

    # Expand the cookiecutter template into the target directory
    expand_template(
        template_path,
        target_dir=project_dir,
        project_name=project_name,
        create_project_dir=create_project_dir,
        kwargs=kwargs,
    )
    if not project_dir.exists():
        print_colored(f"Error: Project '{project_name}' was not created.", Colors.RED)
        sys.exit(1)

    # Change to project directory
    os.chdir(project_dir)

    # Create secrets files if requested
    if create_pypirc:
        create_secrets_file(project_dir, ".pypirc", TOKEN_NAMES, PYPIRC_FILE_TEMPLATE)

    if create_local_env:
        create_secrets_file(project_dir, ".env", TOKEN_NAMES, ENV_FILE_TEMPLATE)

    # Install dependencies
    if install_deps:
        print_colored("Installing dependencies...", Colors.BLUE)
        try:
            run_command(["poetry", "install"], extra_env={"POETRY_VIRTUALENVS_IN_PROJECT": "true"})
        except subprocess.CalledProcessError:
            print_colored("Warning: Poetry install failed", Colors.YELLOW)

    # Initialize Git
    if init_git:
        print_colored("Initializing Git repository...", Colors.BLUE)

        try:
            run_command(["git", "init"])
            run_command(["git", "add", "."])
            run_command(["git", "commit", "-m", "Initial commit"])
        except subprocess.CalledProcessError:
            print_colored("Warning: Git initialization failed", Colors.YELLOW)

        # Create GitHub repository
        if create_github:
            print_colored("Creating GitHub repository...", Colors.BLUE)

            if check_github_cli() and (github_username := get_github_username()):
                full_repo_name = f"{github_username}/{project_name}"

                # Determine repository visibility
                if create_public:
                    repo_visibility = "--public"
                    print_colored("Creating public GitHub repository...", Colors.BLUE)
                else:
                    repo_visibility = "--private"
                    print_colored("Creating private GitHub repository...", Colors.BLUE)

                # Check if repo already exists
                if check_github_repo_exists(project_name, github_username):
                    print_colored(f"Repository {full_repo_name} already exists.", Colors.YELLOW)
                    print_colored("Skipping repository creation, will use existing repository.", Colors.YELLOW)

                    # Add existing repo as remote if not already added
                    try:
                        run_command(
                            ["git", "remote", "add", "origin", f"git@github.com:{github_username}/{project_name}.git"]
                        )
                    except Exception:
                        print_colored("Remote 'origin' already exists, skipping adding remote.", Colors.YELLOW)
                else:
                    # Repo doesn't exist, create it
                    try:
                        run_command(
                            ["gh", "repo", "create", project_name, repo_visibility, "--source=.", "--remote=origin"]
                        )
                    except subprocess.CalledProcessError:
                        print_colored("Error: Failed to create GitHub repository", Colors.RED)
                        sys.exit(1)

                # Push to repository
                try:
                    run_command(["git", "push", "-u", "origin", "main"])
                except subprocess.CalledProcessError:
                    try:
                        run_command(["git", "push", "-u", "origin", "master"])
                    except subprocess.CalledProcessError:
                        print_colored("Warning: Failed to push to repository", Colors.YELLOW)

                print_colored(f"GitHub repository created: https://github.com/{full_repo_name}", Colors.GREEN)

                # Create secrets if requested
                if create_secrets:
                    create_github_secrets(full_repo_name, TOKEN_NAMES)
            else:
                print_colored("GitHub repository creation failed due to CLI issues.", Colors.RED)
        elif create_secrets:
            print_colored("Warning: --secrets requires --github flag", Colors.YELLOW)

    # Success message
    print_colored(f"Project '{project_name}' has been successfully created!", Colors.GREEN)
    print("To start working on your project:")
    print(f"  cd {project_name}")
    print("  make venv")

    # Provide helpful tips
    if create_github and not create_secrets:
        print()
        print_colored("💡 Tip: Add --secrets flag to automatically create repository secrets", Colors.BLUE)

    if not create_local_env and (create_secrets or create_github):
        print_colored("💡 Tip: Add --local-env flag to create .env for local publishing", Colors.BLUE)

    if create_github and not create_public:
        print_colored(
            "💡 Tip: Repository created as private. Use --public next time for public repositories", Colors.BLUE
        )

    if create_local_env or create_secrets:
        print()
        print("🚀 Your project is ready for publishing!")
        print("  Manual:")
        print("      make build")
        print("      make publish-test   # Test on TestPyPI")
        print("      make publish        # Publish to PyPI")
        print("  CI:")
        print("      Commit your lastest changes and do:")
        print("      make release-alpha  # For alpha releases")
        print("      make release-beta   # For beta releases")
        print("      make release-rc     # For release candidate releases")
        print("      make release-micro  # For patch releases")
        print("      make release-minor  # For minor releases")
        print("      make release-major  # For major releases")
        print("      git push && git push --tags")


def expand_template(
    template_path: Path,
    target_dir: Path,
    project_name: str,
    *,
    create_project_dir: bool = False,
    kwargs: Optional[dict] = None,
) -> None:

    cookiecutter_cmd = [
        "cookiecutter",
        str(template_path),
        f"project_name={project_name}",
        "--no-input",
    ]

    for key, value in (kwargs or {}).items():
        cookiecutter_cmd.append(f"{key}={value}")

    # ✅ Case 1: Let Cookiecutter create the directory
    if create_project_dir:
        try:
            run_command(cookiecutter_cmd)
            return
        except subprocess.CalledProcessError:
            print_colored("Error: Failed to generate project", Colors.RED)
            sys.exit(1)

    # ✅ Case 2: Expand into existing directory
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        cmd = cookiecutter_cmd + ["--output-dir", str(tmp_path)]

        try:
            run_command(cmd)
        except subprocess.CalledProcessError:
            print_colored("Error: Failed to generate project", Colors.RED)
            sys.exit(1)

        generated_dir = tmp_path / project_name
        if not generated_dir.exists():
            print_colored("Error: Generated project directory not found", Colors.RED)
            sys.exit(1)

        for item in generated_dir.iterdir():
            dest = target_dir / item.name
            if dest.exists():
                print_colored(f"Error: Cannot move {item.name}, destination already exists", Colors.RED)
                sys.exit(1)
            shutil.move(str(item), str(dest))


def missing_enviroment_secrets(secrets: List[str]) -> List[str]:
    """Check if required environment variables for secrets are set."""
    missing_vars = [var for var in secrets if not os.environ.get(var)]
    return missing_vars


def create_secrets_file(project_dir: Path, secrets_file: str, secrets: List[str], secrets_file_template: str) -> None:
    """Create a secrets file from environment variables."""
    print_colored(f"Creating {secrets_file} file in {project_dir} from environment variables...", Colors.BLUE)

    secrets_file_path = project_dir / secrets_file
    if secrets_file_path.exists():
        print_colored(
            f"  ⚠️  {secrets_file} already exists at {secrets_file_path}, refusing to overwrite", Colors.YELLOW
        )
        return

    tokens = {}
    token_found = {}
    for secret_name in secrets:
        secret_value = os.environ.get(secret_name)
        token_key = secret_name.lower()
        if secret_value:
            tokens[token_key] = secret_value
            token_found[token_key] = True
            if token_key in secrets_file_template:
                print_colored(f"  ✅ Added {secret_name} token to {secrets_file_path}", Colors.GREEN)
        else:
            tokens[token_key] = f"your-{token_key.replace('_', '-')}-here"
            token_found[token_key] = False
            print_colored(
                f"  ⚠️  No {secret_name} found in environment, creating {secrets_file} with placeholder", Colors.YELLOW
            )

    # Write secrets file with restricted permissions
    secrets_file_path.write_text(secrets_file_template.format(**tokens))
    secrets_file_path.chmod(0o600)

    if all(token_found.values()):
        print_colored(f"{secrets_file} file created successfully at {secrets_file_path}", Colors.GREEN)
    else:
        print_colored(
            f"{secrets_file} template created at {secrets_file_path} - please update with your actual tokens",
            Colors.YELLOW,
        )


def create_github_secrets(
    project_name: str,
    secrets: List[str],
) -> None:
    """Create GitHub repository secrets from environment variables."""
    print_colored("Creating GitHub repository secrets...", Colors.BLUE)

    created_count = 0
    skipped_count = 0

    for secret_name in secrets:
        secret_value = os.environ.get(secret_name)

        if not secret_value:
            print_colored(f"  ⚠️  Skipping {secret_name} (not defined in environment)", Colors.YELLOW)
            skipped_count += 1
            continue

        try:
            # Create the secret in GitHub repository
            run_command(["gh", "secret", "set", secret_name, "--repo", project_name], input=secret_value)
            print_colored(f"  ✅ Created secret: {secret_name}", Colors.GREEN)
            created_count += 1
        except subprocess.CalledProcessError:
            print_colored(f"  ❌ Failed to create secret: {secret_name}", Colors.RED)
            skipped_count += 1

    print_colored(f"Secrets summary: {created_count} created, {skipped_count} skipped", Colors.BLUE)
    if skipped_count == 0 and created_count > 0:
        print_colored("All repository secrets created successfully!", Colors.GREEN)
        print_colored(
            f"You can view them at: https://github.com/{project_name}/settings/secrets/actions", Colors.GREEN
        )


def check_github_cli() -> bool:
    """Check if GitHub CLI is available and authenticated."""
    try:
        run_command(["gh", "repo", "list"])
        return True
    except FileNotFoundError:
        print_colored("Error: GitHub CLI (gh) not installed.", Colors.RED)
        print_colored("Install it from: https://cli.github.com/", Colors.RED)
        return False
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.lower().strip() if e.stderr else ""
        stdout = e.stdout.lower().strip() if e.stdout else ""
        combined_output = f"{stdout}\n{stderr}"
        if "not logged into" in combined_output or "authentication" in combined_output:
            print_colored("Error: GitHub CLI not authenticated.", Colors.RED)
            print_colored("Run: gh auth login", Colors.RED)
        elif "network" in combined_output or "connection" in combined_output:
            print_colored("Error: Network connection issues.", Colors.RED)
            print_colored("Check your internet connection and try again.", Colors.RED)
        else:
            print_colored("Error: GitHub CLI check failed.", Colors.RED)
            print_colored("Run: gh auth status", Colors.RED)
            if e.stderr:
                print_colored(f"Details: {e.stderr.strip()}", Colors.RED)

        return False


def get_github_username() -> Optional[str]:
    """Get the currently authenticated GitHub username."""
    try:
        result = run_command(["gh", "api", "user", "--jq", ".login"], check=False)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def check_github_repo_exists(repo_name: str, username: str) -> bool:
    """
    Check if a GitHub repository exists under the authenticated user's account.

    Args:
        repo_name: Name of the repository
        username: GitHub username to check ownership

    Returns:
        True if the repository exists, False otherwise
    """
    try:
        result = run_command(["gh", "repo", "view", f"{username}/{repo_name}"], check=False)
        return result.returncode == 0
    except Exception:
        return False


def read_json_file(config_path: Path) -> Dict:
    """
    Read a configuration file and return its contents as a dictionary.

    Args:
        config_path (Path): Path to the configuration file.

    Returns:
        Dict: Configuration data as a dictionary.
    """
    if not config_path.exists():
        print_colored(f"Error: Configuration file not found at {config_path}", Colors.RED)
        sys.exit(1)

    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print_colored(f"Error reading json configuration file: {e}", Colors.RED)
        sys.exit(1)


def read_ymal_file(config_path: Path) -> Dict:
    """
    Read a YAML configuration file and return its contents as a dictionary.

    Args:
        config_path (Path): Path to the YAML configuration file.

    Returns:
        Dict: Configuration data as a dictionary.
    """
    if not config_path.exists():
        return {}

    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print_colored(f"Error reading YAML configuration file: {e}", Colors.RED)
        sys.exit(1)


def overwrite_default_values(default_config: Dict, user_config: Dict) -> Dict:
    """
    Overwrite default configuration values with user-provided values.
    Args:
        default_config (dict): The default configuration dictionary.
        user_config (dict): The user-provided configuration dictionary.
    Returns:
        Dict: The updated configuration dictionary with user values applied.
    """
    if not isinstance(default_config, dict):
        raise ValueError("Default configuration must be a dictionary.")
    if not isinstance(user_config, dict):
        raise ValueError("User configuration must be a dictionary.")

    updated_config = default_config.copy()
    updated_config.update(user_config)
    return updated_config


def build_menu_from_config(parser: argparse.ArgumentParser, config: Dict) -> None:
    """
    Build a menu from the provided configuration dictionary.

    Args:
        parser (argparse.ArgumentParser): The argument parser to which the menu will be added.
        config (dict): A dictionary containing the menu configuration.
    """
    if not isinstance(config, dict):
        raise ValueError("Config must be a dictionary.")

    for key, value in config.items():
        if not isinstance(value, str):
            raise ValueError(f"Invalid configuration for key '{key}': expected string value.")
        parser.add_argument(f"--{key}", type=str, default=value, help=f"Set {key} (default: {value})")


def update_config_file(user_config_file_path: Path, cookiecutter_config: Dict, user_config: Dict, args: Dict) -> None:
    """
    Update the user configuration file with the provided values.

    Args:
        user_config_file_path (Path): Path to the user configuration file.
        cookiecutter_config (dict): The cookiecutter configuration.
        user_config (dict): The current user configuration.
        args (dict): Values to update the configuration.
    """
    updated_config = user_config.copy()
    for key, value in args.items():
        if key == "project_name":
            continue
        if key in cookiecutter_config and value is not None:
            updated_config[key] = value

    try:
        with open(user_config_file_path, "w") as f:
            yaml.dump({"default_context": updated_config}, f)
    except yaml.YAMLError as e:
        print_colored(f"Error writing configuration file: {e}", Colors.RED)
        sys.exit(1)


# Main epilog
MAIN_EPILOG = """
Available Commands:
  generate    Create a new Python project with Poetry, testing, and CI/CD
  config      Configure default values for project generation

Quick Start:
  %(prog)s generate my-project                     # Create a new project
  %(prog)s config --author_name "Your Name"        # Set default author

For detailed help on each command:
  %(prog)s generate --help
  %(prog)s config --help

Documentation:
  https://generate-project.readthedocs.io/
"""

# Generate command epilog
GENERATE_EPILOG = """
Publishing Setup:
  The script can set up both automated and manual publishing. Requires .env file with tokens.:
  TEST_PYPI_TOKEN=pypi-...      Token for TestPyPI publishing
  PYPI_TOKEN=pypi-...           Token for PyPI publishing
  RTD_TOKEN=rtd_...             Token for ReadTheDocs publishing

  GitHub Secrets (--secrets):
  - Creates GitHub repository secrets from .env tokens

Examples:
  %(prog)s my-project                                                # Basic project
  %(prog)s --local-env my-project                                    # Create local .env file with auth tokens
  %(prog)s --github my-project                                       # Create GitHub repo
  %(prog)s --public my-project                                       # Public GitHub repo
  %(prog)s --public --secrets my-project                             # Public GitHub repo with secrets
  %(prog)s --public --secrets --local-env my-project                 # Full setup

The project directory will be created in the current working directory. If you want to generate the project in the current
directory, use '.' as the project name:
  %(prog)s .                                                         # Create project in current directory

You can create the project directory first and have a project specific .env file in it to avoid using a global .env file
"""

# Config command epilog
CONFIG_EPILOG = """
Configuration File:
  Settings are saved to the installed package's templates/config.yaml file
  Location varies by installation (e.g., venv/lib/python*/site-packages/generate_project/templates/config.yaml)
  All values are used as defaults for the 'generate' command

Examples:
  %(prog)s --author_name "John Doe"                # Set default author
  %(prog)s --author_email "john@example.com"       # Set default email
  %(prog)s --github_username "johndoe"             # Set GitHub username
  %(prog)s --python_version "^3.11"                # Set Python version

  # Set multiple values at once
  %(prog)s --author_name "Jane Smith" --author_email "jane@example.com"

  # To find the config file location do:

<bash>
python -c \"""
import generate_project.main
from pathlib import Path
print()
print(Path(generate_project.main.__file__).parent / 'templates' / 'config.yaml')
\"""
"""


def print_args(**kwargs: Optional[Dict]) -> None:
    """Print the arguments for debugging."""
    print_colored("Arguments received:", Colors.YELLOW)
    for key, value in kwargs.items():
        print_colored(f"  {key}: {value}", Colors.YELLOW)


def main() -> None:
    # Read configuration files
    global_config_file_path = Path(__file__).parent / "templates" / "poetry-template" / "cookiecutter.json"
    cookiecutter_config = read_json_file(global_config_file_path)
    user_config_file_path = Path(__file__).parent / "templates" / "config.yaml"
    user_config = read_ymal_file(user_config_file_path).get("default_context", {})
    config = overwrite_default_values(cookiecutter_config, user_config)

    # Create main parser
    parser = argparse.ArgumentParser(
        description="Create and configure Python projects managed with Poetry.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=MAIN_EPILOG,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    # Create subparsers
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="{generate,config}",
    )

    # Create the generate subparser
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate a new Python project",
        description="Create a new Python project managed with Poetry.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=GENERATE_EPILOG,
    )

    # Add project name as positional argument to generate command
    generate_parser.add_argument("project_name", help="Name of the project to create")

    # Add project configuration arguments to generate parser
    build_menu_from_config(generate_parser, config)

    # Add behavior flags to generate parser
    generate_parser.add_argument(
        "--no-install", dest="install_deps", action="store_false", help="Skip installing dependencies"
    )
    generate_parser.add_argument("--no-git", dest="init_git", action="store_false", help="Skip Git initialization")

    # Add GitHub integration flags to generate parser
    generate_parser.add_argument(
        "--github",
        dest="create_github",
        action="store_true",
        help="Create private GitHub repository (requires gh CLI)",
    )
    generate_parser.add_argument(
        "--public",
        dest="create_public",
        action="store_true",
        help="Create public GitHub repository (implies --github)",
    )
    generate_parser.add_argument(
        "--secrets", dest="create_secrets", action="store_true", help="Create GitHub repository secrets from .env"
    )

    # Add publishing setup flags to generate parser
    generate_parser.add_argument(
        "--pypirc", dest="create_pypirc", action="store_true", help="Create .pypirc file with publishing tokens"
    )
    generate_parser.add_argument(
        "--local-env",
        dest="create_local_env",
        action="store_true",
        help="Create a local .env file with publishing tokens",
    )

    # Add file path arguments to generate parser
    generate_parser.add_argument("--env", dest="env_file", type=Path, help="Use specific .env file (default: ./.env)")
    generate_parser.add_argument("--template", dest="template_path", type=Path, help="Use a specific template path")

    # Create the config subparser
    config_parser = subparsers.add_parser(
        "config",
        help="Configure default project parameters",
        description="Set default values for project configuration parameters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=CONFIG_EPILOG,
    )

    # Add only project configuration arguments to config parser
    build_menu_from_config(config_parser, config)

    # Parse arguments
    args = parser.parse_args()

    # Handle case where no command is provided
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # Handle config command
    if args.command == "config":
        # print_args(**args.__dict__)
        update_config_file(user_config_file_path, cookiecutter_config, user_config, args.__dict__)
        print_colored("Configuration updated successfully!", Colors.GREEN)
        print_colored(f"Updated file: {user_config_file_path}", Colors.GREEN)
        sys.exit(0)

    # Handle generate command
    elif args.command == "generate":
        # Set defaults that depend on script location
        if args.env_file is None:
            args.env_file = find_dotenv(usecwd=True)
        if args.template_path is None:
            args.template_path = Path(__file__).parent / "templates" / "poetry-template"

        # --public or --secrets implies --github
        if args.create_public or args.create_secrets:
            args.create_github = True

        # Generate the project
        # print_args(**args.__dict__)
        generate_project(**args.__dict__)


if __name__ == "__main__":
    main()
