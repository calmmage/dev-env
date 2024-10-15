import re
from pathlib import Path

from git import Repo, GitCommandError
from loguru import logger

# todo: make this configurable? via env var?
DEV_ENV_DIR = Path.home() / ".calmmage" / "dev_env"


def git_pull_with_fetch(repo):
    """
    Fetch and pull updates for the given repository.
    Only report if there were actual changes.
    """
    try:
        # logger.debug("Updating updates...")
        repo.git.fetch("--all")

        # Check if there are changes to pull
        local_commit = repo.head.commit
        current_branch = repo.active_branch.name
        remote_commit = repo.refs[f"origin/{current_branch}"].commit

        repo_name = Path(repo.working_tree_dir).name

        if local_commit != remote_commit:
            # logger.debug("Pulling updates...")
            pull_info = repo.git.pull()
            logger.info(f"Repository {repo_name} has been updated")
            logger.debug(f"Pull info: {pull_info}")
        else:
            logger.debug(f"Repository {repo_name} is already up to date")

        return local_commit != remote_commit
    except Exception as e:
        logger.error(f"Failed to update repository: {repo}: {e}")
        raise RuntimeError(f"Failed to update repository: {e}")


def clone_or_update_dev_env():
    if DEV_ENV_DIR.exists():
        logger.info("Checking dev_env repository for updates")
        try:
            repo = Repo(DEV_ENV_DIR)
            updated = git_pull_with_fetch(repo)
            if updated:
                logger.info("dev_env repository has been updated")
            else:
                logger.info("dev_env repository is already up to date")
        except GitCommandError as e:
            logger.error(f"Failed to update dev_env repository: {e}")
            raise RuntimeError(f"Failed to update dev_env repository: {e}")
    else:
        logger.info("Cloning dev_env repository")
        try:
            Repo.clone_from("https://github.com/calmmage/dev-env.git", str(DEV_ENV_DIR))
            logger.info("dev_env repository has been cloned successfully")
        except GitCommandError as e:
            logger.error(f"Failed to clone dev_env repository: {e}")
            raise RuntimeError(f"Failed to clone dev_env repository: {e}")


def add_line_to_shell_profile_safe(line, shell_profile=Path.home() / ".zshrc"):
    """
    Safely add a line to the shell profile if it doesn't already exist.
    """
    shell_profile = Path(shell_profile)
    if not shell_profile.exists():
        shell_profile.touch()

    with open(shell_profile, "r") as f:
        content = f.read()

    if line in content:
        logger.debug(f"Line already exists in {shell_profile}: {line}")
        return False

    with open(shell_profile, "a") as f:
        f.write(f"\n{line}")
    logger.info(f"Added new line to {shell_profile}: {line}")
    return True


def add_variable_to_shell_profile_safe(variable, value, shell_profile=Path.home() / ".zshrc"):
    """
    Safely add or update a variable in the shell profile.
    """
    shell_profile = Path(shell_profile)
    if not shell_profile.exists():
        shell_profile.touch()

    with open(shell_profile, "r") as f:
        content = f.read()

    new_line = f"export {variable}={value}"
    pattern = re.escape(f"export {variable}=") + r".*"
    match = re.search(pattern, content, re.MULTILINE)

    if match:
        existing_line = match.group(0)
        if existing_line != new_line:
            logger.warning(f"Existing variable differs in {shell_profile}: {existing_line}")
            if input(f"Do you want to update {variable}? (y/n): ").lower() == "y":
                updated_content = re.sub(pattern, new_line, content, flags=re.MULTILINE)
                with open(shell_profile, "w") as f:
                    f.write(updated_content)
                logger.info(f"Updated variable in {shell_profile}: {new_line}")
                return True
        else:
            logger.debug(f"Variable already exists and is up to date in {shell_profile}: {new_line}")
    else:
        with open(shell_profile, "a") as f:
            f.write(f"\n{new_line}")
        logger.info(f"Added new variable to {shell_profile}: {new_line}")
        return True

    return False


def update_shell_profiles():
    # zshrc
    add_variable_to_shell_profile_safe("CALMMAGE_DEV_ENV_PATH", str(DEV_ENV_DIR))
    add_variable_to_shell_profile_safe("CALMMAGE_POETRY_ENV_PATH", "$(poetry env info --path)")
    add_line_to_shell_profile_safe(f"source $CALMMAGE_DEV_ENV_PATH/resources/shell_profiles/.zshrc")
    add_line_to_shell_profile_safe(f"source $CALMMAGE_DEV_ENV_PATH/resources/shell_profiles/.alias")

    # zprofile
    add_variable_to_shell_profile_safe(
        "CALMMAGE_DEV_ENV_PATH", str(DEV_ENV_DIR), shell_profile=Path.home() / ".zprofile"
    )
    add_variable_to_shell_profile_safe(
        "CALMMAGE_POETRY_ENV_PATH", "$(poetry env info --path)", shell_profile=Path.home() / ".zprofile"
    )
    add_line_to_shell_profile_safe(
        f"source $CALMMAGE_DEV_ENV_PATH/resources/shell_profiles/.zshrc", shell_profile=Path.home() / ".zprofile"
    )
    add_line_to_shell_profile_safe(
        f"source $CALMMAGE_DEV_ENV_PATH/resources/shell_profiles/.alias", shell_profile=Path.home() / ".zprofile"
    )
