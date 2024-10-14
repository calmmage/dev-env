import re
from pathlib import Path

import typer
from git import Repo, GitCommandError
from loguru import logger

# todo: make this configurable?
DEV_ENV_DIR = Path.home() / ".calmmage" / "dev_env"
ZSHRC_PATH = Path.home() / ".zshrc"


def clone_or_update_dev_env():
    if DEV_ENV_DIR.exists():
        logger.info("Updating dev_env repository")
        try:
            repo = Repo(DEV_ENV_DIR)
            origin = repo.remotes.origin
            origin.pull()
        except GitCommandError as e:
            logger.error(f"Failed to update dev_env repository: {e}")
            raise typer.Exit(code=1)
    else:
        logger.info("Cloning dev_env repository")
        try:
            Repo.clone_from("https://github.com/calmmage/dev-env.git", str(DEV_ENV_DIR))
        except GitCommandError as e:
            logger.error(f"Failed to clone dev_env repository: {e}")
            raise typer.Exit(code=1)


def update_zshrc():
    if not ZSHRC_PATH.exists():
        ZSHRC_PATH.touch()

    with open(ZSHRC_PATH, "r") as zshrc:
        content = zshrc.read()

    lines_to_add = [
        f"export CALMMAGE_DEV_ENV_PATH={DEV_ENV_DIR}",
        f"export CALMMAGE_POETRY_ENV_PATH=$(poetry env info --path)",
        f"source $CALMMAGE_DEV_ENV_PATH/resources/shell_profiles/.zshrc",
        f"source $CALMMAGE_DEV_ENV_PATH/resources/shell_profiles/.alias",
    ]

    updated_content = content

    for line in lines_to_add:
        if line.startswith("export"):
            pattern = re.escape(line.split("=")[0]) + r"=.*"
            match = re.search(pattern, content, re.MULTILINE)
        elif line.startswith("source"):
            pattern = re.escape(line)
            match = re.search(pattern, content, re.MULTILINE)
        else:
            continue  # Skip lines that don't start with export or source

        if match:
            existing_line = match.group(0)
            if existing_line != line:
                logger.warning(f"Existing line differs: {existing_line}")
                if typer.confirm("Do you want to update this line?"):
                    updated_content = re.sub(pattern, line, updated_content, flags=re.MULTILINE)
            else:
                logger.debug(f"Line already exists and is up to date: {line}")
        else:
            logger.info(f"Adding new line to .zshrc: {line}")
            updated_content += f"\n{line}"

    if updated_content != content:
        with open(ZSHRC_PATH, "w") as zshrc:
            zshrc.write(updated_content)
        logger.info("Updated .zshrc")
    else:
        logger.debug("No changes needed in .zshrc")
