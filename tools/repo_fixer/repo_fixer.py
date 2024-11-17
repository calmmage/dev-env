import pyperclip
import subprocess
import typer
from enum import Enum
from loguru import logger
from pathlib import Path
from textwrap import dedent

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


def _add_precommit_tool_if_missing(repo_path: Path, tool_name: str, content: str):
    pre_commit_config_path = repo_path / ".pre-commit-config.yaml"
    if not pre_commit_config_path.exists():
        logger.warning(
            f"No .pre-commit-config.yaml found at {pre_commit_config_path}. Creating. Don't forget to install"
        )

    else:
        # check if vulture is already in it
        # find the line
        # see if it's not commented out
        content = pre_commit_config_path.read_text()
        if tool_name in content:
            tool_line = [line for line in content.splitlines() if tool_name in line][-1]
            if tool_line.strip().startswith("#"):
                logger.info(
                    f"Found {tool_name} in .pre-commit-config.yaml, but it's commented out. Will add {tool_name} anew."
                )
            else:
                logger.warning(f"Seems like {tool_name} is already in .pre-commit-config.yaml. Skipping.")
                return

    with open(pre_commit_config_path, "w") as f:
        f.write(content)


def _add_vulture(repo_path: Path):
    """Add vulture configuration to the repository

    - find .pre-commit-config.yaml
    - check if vulture is already in it
    - if not, add it
    """
    content = dedent(
        """
    - repo: https://github.com/jendrikseipp/vulture
      rev: v2.10
      hooks:
        - id: vulture
    """
    )
    _add_precommit_tool_if_missing(repo_path, "vulture", content)


def _add_black(repo_path: Path):
    content = dedent(
        """
    - repo: https://github.com/psf/black
      rev: stable
      hooks:
        - id: black
    """
    )
    _add_precommit_tool_if_missing(repo_path, "black", content)


def _add_flake8(repo_path: Path):
    content = dedent(
        """
    - repo: https://github.com/PyCQA/flake8
      rev: 6.1.0
      hooks:
        - id: flake8
    """
    )
    _add_precommit_tool_if_missing(repo_path, "flake8", content)


def _add_isort(repo_path: Path):
    content = dedent(
        """
    - repo: https://github.com/PyCQA/isort
      rev: 5.12.0
      hooks:
        - id: isort
    """
    )
    _add_precommit_tool_if_missing(repo_path, "isort", content)


def _add_ruff(repo_path: Path):
    content = dedent(
        """
    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v1.10.0
      hooks:
        - id: ruff
    """
    )
    _add_precommit_tool_if_missing(repo_path, "ruff", content)


def _add_codecov(repo_path: Path):
    # step 1: add to pre-commit
    content = dedent(
        """
    - repo: https://github.com/codecov/codecov-action
      hooks:
        - id: codecov
    """
    )
    _add_precommit_tool_if_missing(repo_path, "codecov", content)

    # step 2: add to pyproject.toml
    pyproject_toml_path = repo_path / "pyproject.toml"
    if not pyproject_toml_path.exists():
        logger.warning(f"No pyproject.toml found at {pyproject_toml_path}. Skipping.")
        return


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
        logger.info(f"Copied new template to clipboard. Opening {pyproject_toml_path} with Sublime.")
        subprocess.run(["subl", pyproject_toml_path])
    else:
        logger.info("Looks like pyproject.toml is up to date. Skipping.")


def _update_dockerfile(repo_path: Path):
    """
    check if old or new style dockerfile
    if old, copy new template to clipboard and open the file with sublime
    """
    # skip for now
    pass


class Settings(BaseSettings):
    root_paths: List[Path] = [
        Path.home() / "work/projects",
        Path.home() / "work/archive",
        Path.home() / "work/experiments",
    ]


settings = Settings()


def _discover_project(project: str) -> Path:
    if Path(project).exists():
        return Path(project)
    else:
        # check for projects with this name in configured root paths
        for root_path in settings.root_paths:
            project_path = root_path / project
            if project_path.exists():
                return project_path


@app.command()
def fix_repo(
    project: str = typer.Argument(..., help="Project"),
    operation: Operation = typer.Option(..., help="Operation to perform"),
):
    """Fix repository according to modern standards"""
    logger.info(f"Fixing repo at {path} with operation {operation}")

    if not path.exists():
        logger.error(f"Path {path} does not exist")
        raise typer.Exit(1)

    if not path.is_dir():
        logger.error(f"Path {path} is not a directory")
        raise typer.Exit(1)

    try:
        if operation == Operation.ADD_VULTURE:
            _add_vulture(path)

        elif operation == Operation.ADD_BLACK:
            # TODO: Implement black integration
            logger.info("Adding black...")
            pass

        elif operation == Operation.UPDATE_YAML_TESTS:
            # TODO: Implement yaml test updates
            logger.info("Updating yaml tests...")
            pass

        elif operation == Operation.UPGRADE_DOCKERFILE:
            # TODO: Implement dockerfile upgrade
            logger.info("Upgrading dockerfile...")
            pass

        elif operation == Operation.UPGRADE_PYPROJECT:
            # TODO: Implement pyproject.toml upgrade
            logger.info("Upgrading pyproject.toml...")
            pass

        elif operation == Operation.INSTALL_PRECOMMIT:
            # TODO: Implement pre-commit setup
            logger.info("Adding pre-commit...")
            pass

        elif operation == Operation.UPGRADE_LIBS:
            # TODO: Implement library upgrades
            logger.info("Upgrading libraries...")
            pass

        elif operation == Operation.RUN_ALL:
            logger.info("Running all operations...")
            # TODO: Run all operations in sequence
            pass

        logger.success(f"Successfully completed operation {operation}")

    except Exception as e:
        logger.error(f"Error during {operation}: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
