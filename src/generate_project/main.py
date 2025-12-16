#!/usr/bin/env python3
"""
Python project generator using cookiecutter templates.
"""

import argparse
import json
import os
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import (
    Dict,
    List,
    Optional,
)

from dotenv import (
    find_dotenv,
    load_dotenv,
)


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
    cmd: List[str], cwd: Optional[Path] = None, check: bool = True, input: Optional[str] = None
) -> subprocess.CompletedProcess:
    """Run a command with error handling."""
    try:
        return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True, input=input)
    except subprocess.CalledProcessError as e:
        print_colored(f"Command failed: {' '.join(cmd)}", Colors.RED)
        if e.stderr:
            print_colored(f"Error: {e.stderr}", Colors.RED)
        raise


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


def create_github_secrets(env_var_to_secret_map: dict[str, str], project_name: str) -> None:
    """Create GitHub repository secrets from environment variables.

    Args:
        env_var_to_secret_map: Dict mapping environment variable names to GitHub secret names
        project_name: Full repository name (owner/repo)
    """
    print_colored("Creating GitHub repository secrets...", Colors.BLUE)

    created_count = 0
    skipped_count = 0

    for env_var, secret_name in env_var_to_secret_map.items():
        secret_value = os.environ.get(env_var)

        if not secret_value:
            print_colored(f"  ⚠️  Skipping {secret_name} ({env_var} not in environment)", Colors.YELLOW)
            skipped_count += 1
            continue

        try:
            # Create the secret in GitHub repository
            run_command(["gh", "secret", "set", secret_name, "--repo", project_name], input=secret_value)
            print_colored(f"  ✅ Created secret: {secret_name} (from {env_var})", Colors.GREEN)
            created_count += 1
        except subprocess.CalledProcessError:
            print_colored(f"  ❌ Failed to create secret: {secret_name}", Colors.RED)
            skipped_count += 1

    print_colored(f"Secrets summary: {created_count} created, {skipped_count} skipped", Colors.BLUE)
    if created_count > 0:
        print_colored("Repository secrets created successfully!", Colors.GREEN)
        print_colored(
            f"You can view them at: https://github.com/{project_name}/settings/secrets/actions", Colors.GREEN
        )


ENV_FILE_TEMPLATE = """# PyPI Authentication for Poetry
# Poetry uses these environment variables for publishing
# Get tokens from: https://pypi.org/manage/account/token/

POETRY_PYPI_TOKEN_PYPI={pypi_token}
POETRY_PYPI_TOKEN_TESTPYPI={test_token}

# ReadTheDocs Token (optional)
# Get from: https://readthedocs.org/accounts/tokens/
RTD_TOKEN=

# GitHub Token (optional, for gh CLI)
# Get from: https://github.com/settings/tokens
GITHUB_TOKEN=
"""


def generate_env_file(project_dir: Path, show_deprecation: bool = False) -> None:
    """Generate .env file from environment variables.

    Args:
        project_dir: Directory where .env file will be created
        show_deprecation: If True, show deprecation warning for --pypirc flag
    """
    if show_deprecation:
        print_colored("⚠️  Warning: --pypirc flag is deprecated and will be removed in v2.0.0", Colors.YELLOW)
        print_colored("   Poetry uses .env files, not .pypirc", Colors.YELLOW)
        print_colored("   In the future, just copy .env.example to .env", Colors.YELLOW)
        print_colored("", Colors.YELLOW)  # Empty line for readability

    print_colored(f"Creating .env file in {project_dir} from environment variables...", Colors.BLUE)

    # Check if we have tokens in environment (support both old and new variable names)
    pypi_token = os.getenv("POETRY_PYPI_TOKEN_PYPI") or os.getenv("PYPI_TOKEN", "")
    test_token = os.getenv("POETRY_PYPI_TOKEN_TESTPYPI") or os.getenv("TEST_PYPI_TOKEN", "")

    if not pypi_token and not test_token:
        print_colored("  ⚠️  No PyPI tokens found in environment", Colors.YELLOW)
        print_colored("     Set POETRY_PYPI_TOKEN_PYPI or PYPI_TOKEN in your environment", Colors.YELLOW)
        print_colored("     Creating .env template - please update with your tokens", Colors.YELLOW)

    env_path = project_dir / ".env"

    # Backup existing file
    if env_path.exists():
        print_colored("  ⚠️  .env already exists, backing up to .env.backup", Colors.YELLOW)
        env_path.rename(project_dir / ".env.backup")

    # Create .env content
    env_content = ENV_FILE_TEMPLATE.format(
        pypi_token=pypi_token or "your-pypi-token-here", test_token=test_token or "your-testpypi-token-here"
    )

    # Write file with restricted permissions
    env_path.write_text(env_content)
    env_path.chmod(0o600)

    if pypi_token:
        print_colored(f"  ✅ Added POETRY_PYPI_TOKEN_PYPI to {env_path}", Colors.GREEN)
    else:
        print_colored("  ℹ️  POETRY_PYPI_TOKEN_PYPI placeholder added (update manually)", Colors.BLUE)

    if test_token:
        print_colored(f"  ✅ Added POETRY_PYPI_TOKEN_TESTPYPI to {env_path}", Colors.GREEN)
    else:
        print_colored("  ℹ️  POETRY_PYPI_TOKEN_TESTPYPI placeholder added (update manually)", Colors.BLUE)

    if pypi_token and test_token:
        print_colored(f".env file created successfully at {env_path}!", Colors.GREEN)
    else:
        print_colored(f".env template created at {env_path} - please update with your actual tokens", Colors.YELLOW)

    print_colored("💡 Tip: Add .env to .gitignore (should already be there)", Colors.BLUE)


def generate_project(
    project_name: str,
    template_path: Path,
    env_file: Path,
    install_deps: bool = True,
    init_git: bool = True,
    create_github: bool = False,
    create_public: bool = False,
    create_secrets: bool = False,
    create_env: bool = False,
    **kwargs: Optional[Dict],
) -> None:
    """Main project generation logic."""
    # Load environment file if needed
    if create_secrets or create_env:
        if not load_dotenv(dotenv_path=env_file, override=True):
            print_colored("Error: Cannot create secrets/.env without environment file", Colors.RED)
            print_colored(f"Expected location: {env_file}", Colors.RED)
            print_colored("Use --env=FILE to specify a different location", Colors.RED)
            sys.exit(1)

    # Ensure template exists
    if not template_path.exists():
        print_colored(f"Error: Cookiecutter template not found at {template_path}", Colors.RED)
        sys.exit(1)

    # Check if project directory already exists
    project_dir = Path(project_name)
    if project_dir.exists():
        print_colored(f"Error: Directory '{project_name}' already exists.", Colors.RED)
        print_colored("Please choose a different project name or remove the existing directory:", Colors.RED)
        print_colored(f"  rm -rf {project_name}/", Colors.RED)
        sys.exit(1)

    # Generate project
    print_colored("Generating project structure...", Colors.BLUE)
    cookiecutter_cmd = [
        "cookiecutter",
        str(template_path),
        f"project_name={project_name}",
        "--no-input",
    ]
    for key, value in (kwargs or {}).items():
        cookiecutter_cmd.append(f"{key}={value}")

    try:
        run_command(cookiecutter_cmd)
    except subprocess.CalledProcessError:
        print_colored("Error: Failed to generate project", Colors.RED)
        sys.exit(1)

    if not project_dir.exists():
        print_colored(f"Error: Project '{project_name}' was not created.", Colors.RED)
        sys.exit(1)

    # Create .env file if requested (before changing directory)
    if create_env:
        # show_deprecation=True if called via --pypirc flag (deprecated)
        generate_env_file(project_dir, show_deprecation=create_env == "deprecated")

    # Change to project directory
    os.chdir(project_dir)

    # Install dependencies
    if install_deps:
        print_colored("Installing dependencies...", Colors.BLUE)
        try:
            run_command(["poetry", "install"])
        except subprocess.CalledProcessError:
            print_colored("Warning: Poetry install failed", Colors.YELLOW)

    # Initialize Git
    if init_git:
        print_colored("Initializing Git repository...", Colors.BLUE)
        run_command(["git", "init"])
        run_command(["git", "add", "."])
        run_command(["git", "commit", "-m", "Initial commit"])

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
                            ["git", "remote", "add", "origin", f"git@github.com:{github_username}/{project_name}.git"],
                            check=False,
                        )
                    except Exception:
                        pass  # Remote might already exist
                else:
                    # Repo doesn't exist, create it
                    run_command(
                        ["gh", "repo", "create", project_name, repo_visibility, "--source=.", "--remote=origin"]
                    )

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
                    # Map new env var names (in .env) to old GitHub secret names (in workflows)
                    env_to_secret_mapping = {
                        "POETRY_PYPI_TOKEN_PYPI": "PYPI_TOKEN",
                        "POETRY_PYPI_TOKEN_TESTPYPI": "TEST_PYPI_TOKEN",
                        "RTD_TOKEN": "RTD_TOKEN",
                    }
                    create_github_secrets(env_to_secret_mapping, full_repo_name)
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

    if not create_env and (create_secrets or create_github):
        print_colored("💡 Tip: Use --pypirc flag to create .env for local publishing", Colors.BLUE)
        print_colored("   (Note: --pypirc is deprecated, just copy .env.example to .env)", Colors.YELLOW)

    if create_github and not create_public:
        print_colored(
            "💡 Tip: Repository created as private. Use --public next time for public repositories", Colors.BLUE
        )

    if create_env or create_secrets:
        print()
        print("🚀 Your project is ready for publishing!")
        print("  Manual:    make build")
        print("             make publish-test  # Test on TestPyPI")
        print("             make publish       # Publish to PyPI")
        print("  Automated: make release-<level>")
        print("             git tag v1.0.0 && git push --tags")


def print_args(**kwargs: Optional[Dict]) -> None:
    """Print the arguments for debugging."""
    print_colored("Arguments received:", Colors.YELLOW)
    for key, value in kwargs.items():
        print_colored(f"  {key}: {value}", Colors.YELLOW)


def read_json_file(config_path: Path) -> dict:
    """
    Read a configuration file and return its contents as a dictionary.

    Args:
        config_path (Path): Path to the configuration file.

    Returns:
        dict: Configuration data as a dictionary.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"Error reading configuration file: {e}")


def read_ymal_file(config_path: Path) -> dict:
    """
    Read a YAML configuration file and return its contents as a dictionary.

    Args:
        config_path (Path): Path to the YAML configuration file.

    Returns:
        dict: Configuration data as a dictionary.
    """

    if not config_path.exists():
        return {}

    try:
        import yaml
    except ImportError:
        raise ImportError("YAML support requires PyYAML. Install it with: pip install pyyaml")

    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise ValueError(f"Error reading YAML configuration file: {e}")


def overwrite_default_values(default_config: dict, user_config: dict) -> dict:
    """
    Overwrite default configuration values with user-provided values.
    Args:
        default_config (dict): The default configuration dictionary.
        user_config (dict): The user-provided configuration dictionary.
    Returns:
        dict: The updated configuration dictionary with user values applied.
    """
    if not isinstance(default_config, dict):
        raise ValueError("Default configuration must be a dictionary.")
    if not isinstance(user_config, dict):
        raise ValueError("User configuration must be a dictionary.")

    updated_config = default_config.copy()
    updated_config.update(user_config)
    return updated_config


def build_menu_from_config(parser: argparse.ArgumentParser, config: dict) -> None:
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


def update_config_file(user_config_file_path: Path, cookiecutter_config: dict, user_config: dict, args: dict) -> None:
    """
    Update the user configuration file with the provided values.

    Args:
        user_config_file_path (Path): Path to the user configuration file.
        cookiecutter_config (dict): The cookiecutter configuration.
        user_config (dict): The current user configuration.
        args (dict): Values to update the configuration.
    """
    try:
        import yaml
    except ImportError:
        raise ImportError("YAML support requires PyYAML. Install it with: pip install pyyaml")

    updated_config = user_config.copy()
    for key, value in args.items():
        if key == "project_name":
            continue
        if key in cookiecutter_config and value is not None:
            updated_config[key] = value

    with open(user_config_file_path, "w") as f:
        yaml.dump({"default_context": updated_config}, f)


EPILOG = """
Publishing Setup:
  The script can set up both automated and manual publishing. Requires .env file with tokens:
  POETRY_PYPI_TOKEN_PYPI=pypi-...           Token for PyPI publishing
  POETRY_PYPI_TOKEN_TESTPYPI=pypi-...       Token for TestPyPI publishing
  RTD_TOKEN=rtd_...                         Token for ReadTheDocs publishing

  GitHub Secrets (--secrets):
  - Creates GitHub repository secrets from .env tokens

  Local Publishing Setup (--pypirc, DEPRECATED):
  - Creates .env file for local publishing (Poetry uses environment variables)
  - Recommended: Just copy .env.example to .env and add your tokens
  - Enables 'make publish-test' and 'make publish'

Examples:
  %(prog)s my-project                              # Basic project
  %(prog)s my-project --github                     # Create GitHub repo
  %(prog)s my-project --public                     # Public GitHub repo
  %(prog)s my-project --public --secrets --pypirc  # Full setup (--pypirc deprecated)
"""


def main() -> None:
    """Main entry point."""
    # Read configuration files
    global_config_file_path = Path(__file__).parent / "templates" / "poetry-template" / "cookiecutter.json"
    cookiecutter_config = read_json_file(global_config_file_path)
    user_config_file_path = Path(__file__).parent / "templates" / "config.yaml"
    user_config = read_ymal_file(user_config_file_path).get("default_context", {})
    config = overwrite_default_values(cookiecutter_config, user_config)

    # Create main parser
    parser = argparse.ArgumentParser(
        description="Create and configure Python projects from cookiecutter templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

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
        description="Create a new Python project from cookiecutter templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EPILOG,
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
        "--pypirc",
        dest="create_env",
        action="store_const",
        const="deprecated",
        help="(DEPRECATED) Create .env file from environment tokens. Use .env.example instead",
    )

    # Add file path arguments to generate parser
    generate_parser.add_argument("--env", dest="env_file", type=Path, help="Use specific .env file (default: ./.env)")
    generate_parser.add_argument("--template", dest="template_path", type=Path, help="Use a specific template path")

    # Create the config subparser
    config_parser = subparsers.add_parser(
        "config",
        help="Configure default project parameters",
        description="Set default values for project configuration parameters",
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
        update_config_file(user_config_file_path, cookiecutter_config, user_config, args.__dict__)
        print_colored("Configuration updated successfully!", Colors.GREEN)
        print_colored(f"Updated file: {user_config_file_path}", Colors.GREEN)
        sys.exit(0)

    # Handle generate command
    elif args.command == "generate":
        # Set defaults that depend on script location
        if args.env_file is None:
            args.env_file = find_dotenv()
        if args.template_path is None:
            args.template_path = Path(__file__).parent / "templates" / "poetry-template"

        # --public implies --github
        if args.create_public:
            args.create_github = True

        # Generate the project
        # print_args(**args.__dict__)
        generate_project(**args.__dict__)


if __name__ == "__main__":
    main()
