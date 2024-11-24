import subprocess
from enum import Enum
from functools import lru_cache
from pathlib import Path
from textwrap import dedent, indent
from typing import List

import pyperclip
import typer
import yaml
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

app = typer.Typer()


class Operation(str, Enum):
    ADD_VULTURE = "add-vulture"
    ADD_BLACK = "add-black"
    UPDATE_YAML_TESTS = "update-yaml-tests"
    UPGRADE_DOCKERFILE = "upgrade-dockerfile"
    UPGRADE_PYPROJECT = "upgrade-pyproject"
    ADD_PRECOMMIT = "add-precommit"
    UPGRADE_LIBS = "upgrade-libs"
    RUN_ALL = "run-all"


class Settings(BaseSettings):
    root_paths: List[Path]
    codecov_fail_under: int = 80

    @classmethod
    def from_yaml(cls, path: Path):
        with open(path) as file:
            config_data = yaml.safe_load(file)

        # Expand user directory for each path in root_paths
        config_data["root_paths"] = [Path(p).expanduser() for p in config_data["root_paths"]]

        return cls(**config_data)


# Initialize settings with the loaded configuration
config_path = Path(__file__).parent / "config.yaml"
settings = Settings.from_yaml(config_path)


def _add_precommit_tool_if_missing(repo_path: Path, tool_name: str, content: str):
    logger.debug(f"Adding pre-commit tool if missing: {tool_name}")
    pre_commit_config_path = repo_path / ".pre-commit-config.yaml"

    content = indent(content, "  ")

    if not pre_commit_config_path.exists():
        logger.warning(
            f"No .pre-commit-config.yaml found at {pre_commit_config_path}. Creating. Don't forget to install"
        )
    else:
        # check if tools is already in it
        # find the line
        # see if it's not commented out
        existing_content = pre_commit_config_path.read_text()
        if tool_name in existing_content:
            tool_line = [line for line in existing_content.splitlines() if tool_name in line][-1]
            if tool_line.strip().startswith("#"):
                logger.info(
                    f"Found {tool_name} in .pre-commit-config.yaml, but it's commented out. Will add {tool_name} anew."
                )
            else:
                logger.warning(
                    f"Seems like {tool_name} is already in .pre-commit-config.yaml. Skipping."
                )
                return
        content = existing_content.rstrip() + "\n" + content

    pre_commit_config_path.write_text(content)


def _add_pyproject_section_if_missing(repo_path: Path, section: str, content: str):
    pyproject_toml_path = repo_path / "pyproject.toml"
    if not pyproject_toml_path.exists():
        logger.warning(f"No pyproject.toml found at {pyproject_toml_path}. Skipping.")
        return
    pyproject_toml_content = pyproject_toml_path.read_text()

    if section in pyproject_toml_content:
        logger.info(f"Section {section} already exists in pyproject.toml. Skipping.")
        return

    pyproject_toml_content = pyproject_toml_content.rstrip() + "\n" + content
    pyproject_toml_path.write_text(pyproject_toml_content)


@lru_cache()
def _get_source_dir_name(repo_path: Path) -> str:
    source_dir_name = repo_path.name
    if not (repo_path / source_dir_name).exists():
        source_dir_name = source_dir_name.replace("-", "_")
    if not (repo_path / source_dir_name).exists():
        # ask user for project name
        source_dir_name = typer.prompt(f"Please provide a source directory name for {repo_path}: ")
        # option 1: user provided full path
        if Path(source_dir_name).exists():
            return Path(source_dir_name).name
        # option 2: user provided name
        if not (repo_path / source_dir_name).exists():
            return None
    return source_dir_name


def _add_vulture(repo_path: Path):
    """Add vulture configuration to the repository

    - find .pre-commit-config.yaml
    - check if vulture is already in it
    - if not, add it
    """

    source_dir_name = _get_source_dir_name(repo_path)

    content = dedent(
        rf"""
        - repo: https://github.com/jendrikseipp/vulture
          rev: 'v2.10'
          hooks:
            - id: vulture
              args: [
              "--min-confidence", "80",
              "--exclude", "**/migrations/*,**/__pycache__/*",
              "{source_dir_name}"  # project_name
              ]
              files: ^.*\.py$
              exclude: ^(.git|.venv|venv|build|dist)/.*$
        """
    )
    _add_precommit_tool_if_missing(repo_path, "vulture", content)


def _add_black(repo_path: Path):
    content = dedent(
        """
        - repo: https://github.com/psf/black
          rev: 24.2.0
          hooks:
            # - id: black
            #   args: [ --line-length=100 ]
            - id: black-jupyter
              name: black-jupyter
              description:
                "Black: The uncompromising Python code formatter (with Jupyter Notebook support)"
              entry: black
              language: python
              minimum_pre_commit_version: 2.9.2
              require_serial: true
              types_or: [python, pyi, jupyter]
              additional_dependencies: [".[jupyter]"]
        """
    )

    _add_precommit_tool_if_missing(repo_path, "black", content)


def _add_flake8(repo_path: Path):
    content = dedent(
        """
          - repo: https://github.com/pycqa/flake8
            rev: '7.0.0'  # Use the latest stable version
            hooks:
              - id: flake8
                additional_dependencies: [
                'flake8-docstrings',
                'flake8-bugbear',
                'flake8-comprehensions',
                'flake8-simplify',
                ]
                args: [
                "--max-line-length=100",
                "--exclude=.git,__pycache__,build,dist",
                "--ignore=E203,W503",  # Ignore some style errors that conflict with other tools
                ]
        """
    )
    _add_precommit_tool_if_missing(repo_path, "flake8", content)


def _add_isort(repo_path: Path):
    content = dedent(
        """
        - repo: https://github.com/PyCQA/isort
          rev: 5.13.2
          hooks:
            - id: isort
              name: isort (python)
        """
    )
    _add_precommit_tool_if_missing(repo_path, "isort", content)

    content = dedent(
        """
        [tool.isort]
        profile = "black"
        multi_line_output = 3
        line_length = 100
        include_trailing_comma = true
        force_grid_wrap = 0
        use_parentheses = true
        ensure_newline_before_comments = true
        skip = [".git", "venv", ".env", "__pycache__"]
        # known_first_party = ["your_package_name"]  # Replace with your package name
        # known_third_party = [
        #     "aiogram",
        #     "fastapi",
        #     "pydantic",
        #     "pytest",
        #     "tqdm",
        #     "loguru"
        # ]
        # sections = [
        #     "FUTURE",
        #     "STDLIB",
        #     "THIRDPARTY",
        #     "FIRSTPARTY",
        #     "LOCALFOLDER"
        # ]
        """
    )
    _add_pyproject_section_if_missing(repo_path, "[tool.isort]", content)


def _add_pyupgrade(repo_path: Path):
    content = dedent(
        """
          - repo: https://github.com/asottile/pyupgrade
            rev: v3.19.0
            hooks:
              - id: pyupgrade
        """
    )
    _add_precommit_tool_if_missing(repo_path, "pyupgrade", content)


def _add_ruff(repo_path: Path):
    content = dedent(
        """
        - repo: https://github.com/astral-sh/ruff-pre-commit
          # Ruff version.
          rev: v0.7.4
          hooks:
            # Run the linter.
            - id: ruff
              types_or: [ python, pyi ]
              args: [ --fix ]
            # Run the formatter.
            - id: ruff-format
              types_or: [ python, pyi ]
        """
    )
    _add_precommit_tool_if_missing(repo_path, "ruff", content)


def _add_codecov(repo_path: Path):
    source_dir_name = _get_source_dir_name(repo_path)

    # step 1: add to pre-commit
    content = dedent(
        f"""
          - repo: local
            hooks:
              - id: pytest-check
                name: pytest-check
                entry: pytest
                language: system
                pass_filenames: false
                always_run: true
                args: [
                "--cov={source_dir_name}",
                "--cov-report=xml",
                "--cov-fail-under={settings.codecov_fail_under}",
                ]
        """
    )
    # - repo: https://github.com/codecov/codecov-action
    #   hooks:
    #     - id: codecov
    _add_precommit_tool_if_missing(repo_path, "pytest-check", content)

    # step 2: add to pyproject.toml
    subprocess.run(["poetry", "add", "--group", "test", "pytest-cov"], cwd=repo_path)


def _update_pyproject_toml(repo_path: Path):
    """
    - Step 1: check if this is old or new style pyproject.toml
    - Step 2: if old, copy new template to clipboard and open the file with sublime
    """
    pyproject_toml_path = repo_path / "pyproject.toml"
    if not pyproject_toml_path.exists():
        logger.warning(f"No pyproject.toml found at {pyproject_toml_path}. Skipping.")
        return

    pyproject_toml_content = pyproject_toml_path.read_text()

    template_path = Path(__file__).parent / "poetry_template.txt"
    template = template_path.read_text()

    # check if it's old or new style
    # old style: doesn't have   [tool.poetry.group.test.dependencies]
    keyword = "[tool.poetry.group.test.dependencies]"
    if keyword not in pyproject_toml_content:
        pyperclip.copy(template)
        logger.info(
            f"Copied new template to clipboard. Opening {pyproject_toml_path} with Sublime."
        )
        subprocess.run(["subl", pyproject_toml_path])
    else:
        logger.info(
            "Looks like pyproject.toml is up to the standard of the latest template. (main, dev, extras, test) Skipping."
        )


def _update_dockerfile(repo_path: Path):
    """
    check if old or new style dockerfile
    if old, copy new template to clipboard and open the file with sublime
    """
    # skip for now
    pass


def _update_yaml_tests(repo_path: Path):
    """Update or create the GitHub Actions workflow file for tests."""
    workflow_dir = repo_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    workflow_file = workflow_dir / "main.yml"

    template_path = Path(__file__).parent / "tests_workflow_template.txt"

    template_content = template_path.read_text()
    workflow_file.write_text(template_content)
    logger.info(f"Updated GitHub Actions workflow file at {workflow_file}.")


def _install_precommit(repo_path: Path):
    """Install pre-commit hooks in the repository."""
    pre_commit_config_path = repo_path / ".pre-commit-config.yaml"
    if not pre_commit_config_path.exists():
        logger.error(
            f"No .pre-commit-config.yaml found at {pre_commit_config_path}. Cannot install pre-commit."
        )
        return

    try:
        subprocess.run(["pre-commit", "install"], cwd=repo_path, check=True)
        logger.info("Pre-commit hooks installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install pre-commit hooks: {e}")


def _discover_project(project: str) -> Path:
    if Path(project).exists():
        return Path(project)
    else:
        # check for projects with this name in configured root paths
        for root_path in settings.root_paths:
            project_path = root_path / project
            if project_path.exists():
                return project_path


def _add_precommit(repo_path: Path):
    _add_black(repo_path)
    _add_vulture(repo_path)
    _add_flake8(repo_path)
    _add_isort(repo_path)
    # _add_ruff(repo_path)
    _add_codecov(repo_path)
    _add_pyupgrade(repo_path)
    _install_precommit(repo_path)


@app.command()
def fix_repo(
    project: str = typer.Argument(..., help="Project"),
    operation: Operation = typer.Option(Operation.RUN_ALL, help="Operation to perform"),
):
    """Fix repository according to modern standards"""
    repo_path = _discover_project(project)
    if repo_path is None:
        logger.error(f"Project {project} not found in any of the root paths: {settings.root_paths}")
        raise typer.Exit(1)

    logger.info(f"Fixing repo at {repo_path} with operation {operation}")

    if not repo_path.is_dir():
        logger.error(f"Path {repo_path} is not a directory")
        raise typer.Exit(1)

    try:
        if operation == Operation.ADD_VULTURE:
            _add_vulture(repo_path)

        elif operation == Operation.ADD_BLACK:
            _add_black(repo_path)

        elif operation == Operation.UPDATE_YAML_TESTS:
            _update_yaml_tests(repo_path)

        elif operation == Operation.ADD_PRECOMMIT:
            # Add all standard tools
            _add_precommit(repo_path)

        elif operation == Operation.UPGRADE_PYPROJECT:
            _update_pyproject_toml(repo_path)

        elif operation == Operation.UPGRADE_DOCKERFILE:
            _update_dockerfile(repo_path)

        elif operation == Operation.RUN_ALL:
            logger.info("Running all operations...")
            _update_pyproject_toml(repo_path)
            _add_precommit(repo_path)
            _update_dockerfile(repo_path)
            _update_yaml_tests(repo_path)

        logger.success(f"Successfully completed operation {operation}")

    except Exception as e:
        logger.error(f"Error during {operation}: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
