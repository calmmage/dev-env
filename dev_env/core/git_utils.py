import time
import traceback
from functools import lru_cache
from pathlib import Path
from typing import Union

from dotenv import load_dotenv
from git import Repo
from github import Github
from github.Repository import Repository
from loguru import logger
from pydantic_settings import BaseSettings

from dev_env.core.constants import experiments_dir, projects_dir, archive_dir
from dev_env.core.settings import settings
from dev_env.setup.setup_shell_profiles_and_env import git_pull_with_fetch

github_client = Github(settings.github_api_token.get_secret_value())


@lru_cache
def get_all_repos() -> list[Repository]:
    return list(github_client.get_user().get_repos())


def check_repo_allowed(repo: Repository):
    full_repo_name = repo.full_name

    if not any([full_repo_name.startswith(team) for team in settings.accounts_to_clone_from]):
        # logger.info(f"Skipping {full_repo_name}")
        return False
    return True


def check_repo_cloned(repo: Repository):
    repo_name = repo.name
    folders_to_check = [
        experiments_dir,
        projects_dir,
        archive_dir,
    ]

    for folder in folders_to_check:
        local_repo_path = folder / repo_name
        if local_repo_path.exists():
            return local_repo_path
    return None


url_keywords = ["http://", "https://", "github.com", "@"]


def parse_repo_name_from_url(url):
    import re

    # Extract the owner and repo name from the URL using regex
    match = re.search(r"github\.com/([^/]+)/([^/]+)\.git", url)
    if match:
        owner = match.group(1)
        repo_name = match.group(2)
        return f"{owner}/{repo_name}"
    else:
        return None


def get_repo(repo_key: str):
    """
    Get repo object from github.
    Args:
        repo_key (str): repo name, full name, or url.
    Returns:
        repo (Repository): repo object.
    """
    if isinstance(repo_key, (Repository, Repo)):
        return repo_key
    if any([keyword in repo_key for keyword in url_keywords]):  # url
        repo = None
        candidates = [r for r in get_all_repos() if r.clone_url == repo_key]
        if len(candidates) == 1:
            repo = candidates[0]

        parsed_name = parse_repo_name_from_url(repo_key)
        if parsed_name:
            if repo and repo.full_name != parsed_name:
                logger.warning(f"Repo {repo} parsed to {parsed_name} but full name is different")
            if repo is None:
                repo = github_client.get_repo(parsed_name)
    elif "/" in repo_key:  # full name
        repo = github_client.get_repo(repo_key)
    else:  # just name
        candidates = [r for r in get_all_repos() if r.name == repo_key]
        user_name = github_client.get_user().login
        # logger.info(f"User name: {user_name}")
        # sort candidates, putting user's repos first
        candidates = sorted(candidates, key=lambda x: x.owner.login == user_name, reverse=True)
        if len(candidates) == 1:
            repo = candidates[0]
        elif len(candidates) > 1:
            print(f"Found {len(candidates)} candidates for {repo_key}: {candidates}")
            repo = candidates[0]
        else:
            print(f"Found no candidates for {repo_key} in {user_name}")
            repo = None
    return repo


def clone_repo(
    repo: Union[str, Repository, Repo], target_dir: Path, repo_name: str = None, pull_if_exists: bool = True
):
    """
    Clone repo from github to target_dir
    Args:
        repo (str): repo name, full name, or url.
        target_dir (Path): target directory.
        repo_name (str): target dir name. If None, use repo name.
        pull_if_exists (bool): if True, pull repo if exists.
    """

    repo = get_repo(repo)
    if repo_name is None:
        repo_name = repo.name
    if target_dir.name != repo_name:
        target_dir = target_dir / repo_name

    # todo: check exists, check empty, check is git repo
    if target_dir.exists():
        if list(target_dir.iterdir()):
            logger.warning(f"Repo {target_dir} already exists")
            # todo: check the remote match
            if pull_if_exists:
                try:
                    local_repo = Repo(target_dir)
                except Exception as e:
                    logger.error(f"Failed to open {target_dir} as git repo: {e}")
                    return None
                try:
                    git_pull_with_fetch(local_repo)
                    # local_repo.remotes.origin.pull()
                    logger.info(f"Pulled changes for {target_dir}")
                    return local_repo
                except Exception as e:
                    logger.error(f"Failed to pull {target_dir}: {e}")
                    return local_repo
        else:
            target_dir.rmdir()

    # todo: will this work with private repos?
    # somehow it worked in notebook -
    try:
        local_repo = Repo.clone_from(repo.clone_url, target_dir)
    except Exception as e:
        logger.error(f"Failed to clone {repo.clone_url} to {target_dir}: {e}")
        return None

    logger.info(f"Cloned {repo.full_name} to {target_dir}")
    return local_repo


def create_and_clone_repo(repo_name: str, target_dir: Path, template_repo_name: str, num_retries: int = 3):
    create_repo_from_template(repo_name, template_repo_name)
    # add retry with backoff
    for i in range(num_retries):
        try:
            return clone_repo(repo_name, target_dir)
        except Exception as e:
            time.sleep(2 ** (i + 1))

            logger.error(f"Failed to clone {repo_name} to {target_dir} on attempt {i}: {e}")
    else:
        logger.error(f"Failed to clone {repo_name} to {target_dir} after {num_retries} attempts")
        traceback.print_exc()
        return None


def get_github_template_names():
    for repo in get_all_repos():
        if repo.is_template:
            yield repo.name


def create_repo_from_template(name, template_name):
    """
    Create a new repo from template.
    Args:
        repo_name (str): new repo name.
        template_repo_key (str): template repo name, full name, or url.
    """
    logger.debug(f"Creating a new repository {name} from the template: {template_name}")
    repo = get_repo(template_name)

    # if template_name not in templates:
    if not repo.is_template:
        templates = list(get_github_template_names())
        raise ValueError(f"Invalid template name: {template_name}. Available templates: {templates}")
    # check if the repo already exists
    if name in [repo.name for repo in get_all_repos()]:
        raise ValueError(f"Repository already exists: https://github.com/{repo.full_name}")

    username = github_client.get_user().login
    github_client._Github__requester.requestJsonAndCheck(
        "POST",
        f"/repos/{repo.full_name}/generate",
        input={"owner": username, "name": name},
    )
    url = f"https://github.com/{username}/{name}"
    logger.debug(f"Repository created: {url}")
    # return the repo link ?
    return url


class Settings(BaseSettings):
    github_api_token: str


def get_github_client() -> Github:
    """Initialize and return a GitHub client."""
    load_dotenv()
    settings = Settings()
    return Github(settings.github_api_token)


def is_git_repo(path: Path) -> bool:
    """Check if the given path is a git repository."""
    return (path / ".git").is_dir()
