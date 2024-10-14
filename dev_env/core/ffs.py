from datetime import datetime
from loguru import logger
from pathlib import Path
from github import Github
from typing import Union
from github.Repository import Repository
from git import Repo
from dev_env.core.settings import settings
from dev_env.core.constants import (
    all_projects_dirs,
    seasonal_dir,
    archive_dir,
    projects_dir,
    experiments_dir,
    contexts_dir,
)

# plan:
# idea 1: create all projects dirs
# idea 2: clone all projects - if exists, pull
# idea 3: script to set up seasonal folder
# idea 4 - set up ~/.calmmage dir
# idea 5 - build zshrc file
# idea 6 - set up ~/code dir - softlinks to key locations
# idea 7, essential - daily job

# class MyDevEnv:
#     def __init__(self, **kwargs):
#         self.settings = MySettings(**kwargs)
#         self._github_client = None

#     @property
#     def github_client(self):
#         if self._github_client is None:
#             self._github_client = Github(self.settings.github_api_token)
#         return self._github_client

#     def setup(self):
#         self.create_dirs()
#         self.clone_projects()


# region  idea 1


def create_dirs():
    settings.root_dir.mkdir(parents=True, exist_ok=True)
    settings.symlinks_dir.mkdir(parents=True, exist_ok=True)
    settings.env_dir.mkdir(parents=True, exist_ok=True)

    for dir_path in all_projects_dirs:
        # for dir in settings.structural_dirs:
        # dir_path = settings.root_dir / dir
        if not dir_path.exists():
            dir_path.mkdir()


# endregion

# region idea 2 - clone projects

github_client = Github(settings.github_api_token.get_secret_value())


# todo: move to utils
def get_all_repos():
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


def clone_projects():
    # list all projects in my github
    # select only the ones in the accounts_to_clone_from
    # clone main projects to projects dir
    # clone other projects to archive dir

    # logic 1: what to do if dir exists - pull
    # logic 2: first check if repo is cloned _somewhere_
    # main repos -> move to projects dir
    # others -> don't touch

    repos_list = get_all_repos()
    for repo in repos_list:
        if not check_repo_allowed(repo):
            continue

        # check if repo is cloned somewhere in main dirs
        local_repo_path = check_repo_cloned(repo)
        if local_repo_path:
            # first, check if it's a main repo that is not in projects dir
            if repo.name in settings.main_repos:
                if local_repo_path.parent != projects_dir:
                    logger.warning(f"Main repo {local_repo_path} is not in {projects_dir}")
                    logger.info(f"Moving {local_repo_path} to {projects_dir}")
                    local_repo_path.rename(projects_dir / local_repo_path.name)
                    local_repo_path = projects_dir / local_repo_path.name

            # just pull
            local_repo = Repo(local_repo_path)
            try:
                pull_info = local_repo.remotes.origin.pull()
                if pull_info:
                    logger.info(f"Pulled changes for {local_repo_path}: {pull_info}")
                else:
                    logger.debug(f"No changes to pull for {local_repo_path}")
            except Exception as e:
                logger.error(f"Failed to pull {local_repo_path}: {e}")
            continue

        # clone
        # determine target dir
        # if created in last month -> experiments
        # if in main repos -> projects
        # else -> archive

        repo_creation_date = repo.created_at
        if repo_creation_date > datetime.now() - timedelta(days=30):
            target_dir = experiments_dir
        elif repo.name in settings.main_repos:
            target_dir = projects_dir
        else:
            target_dir = archive_dir

        target_path = target_dir / repo.name


# endregion idea 2 - clone projects

# region idea 3 - seasonal folder

#
# seasonal/
# ├── yy-mm-mmm
# ├── ── dev-yy-mm (git, poetry)
# ├── ── ── draft [THIS IS MAIN ENTRY POINT]
# ├── ── ── wip
# ├── ── ── paused
# ├── ──p1 (git, poetry)
# ├── ──p2 ...
# ├── yy-mm-mmm
# ├── latest

# a) need a github repo template for dev-seasonal dir - simple: poetry, cursor workspace, draft, wip, paused
# b) softlink seasonal folder to latest
# c)
# d) 'new_project' tool -
# - option 1: draft -> seasonal folder
# - option 2: project -> always a git repo -> seasonal folder AND experiments folder
all_repos = get_all_repos()


# todo: move to utils
def create_repo_from_template(repo_name: str, template_repo_key: str):
    """
    Create a new repo from template.
    Args:
        repo_name (str): new repo name.
        template_repo_key (str): template repo name, full name, or url.
    """
    template_repo = get_repo(template_repo_key)
    if not template_repo.is_template:
        raise ValueError(f"Template repo {template_repo_key} is not a template")

    # check if repo exists
    user = github_client.get_user()
    if any([repo.full_name == f"{user.name}/{repo_name}" for repo in all_repos]):
        raise ValueError(f"Repo {repo_name} already exists")
    return user.create_repo(repo_name, template_repo)


url_keywords = ["http://", "https://", "github.com", "@"]


def parse_repo_name_from_url(url):
    import re
    # Extract the owner and repo name from the URL using regex
    match = re.search(r'github\.com/([^/]+)/([^/]+)\.git', url)
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
        candidates = [r for r in all_repos if r.clone_url == repo_key]
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
        candidates = [r for r in all_repos if r.name == repo_key]
        user_name = github_client.get_user().login
        logger.info(f"User name: {user_name}")
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


# todo: move to utils
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
        logger.warning(f"Repo {target_dir} already exists")
        # todo: check the remote match
        if pull_if_exists:
            try:
                local_repo = Repo(target_dir)
            except Exception as e:
                logger.error(f"Failed to open {target_dir} as git repo: {e}")
                return None
            try:
                local_repo.remotes.origin.pull()
                logger.info(f"Pulled changes for {target_dir}")
                return local_repo
            except Exception as e:
                logger.error(f"Failed to pull {target_dir}: {e}")
                return local_repo

    # todo: will this work with private repos?
    # somehow it worked in notebook -
    try:
        local_repo = Repo.clone_from(repo.clone_url, target_dir)
    except Exception as e:
        logger.error(f"Failed to clone {repo.clone_url} to {target_dir}: {e}")
        return None


# todo: move to utils
def create_and_clone_repo(repo_name: str, target_dir: Path, template_repo_name: str):
    create_repo_from_template(repo_name, template_repo_name)
    clone_repo(repo_name, target_dir)


def setup_seasonal_folder(dt: datetime = None):
    """
    Create a new seasonal folder and populate it with a dev repo from template.
    Link seasonal folder to latest.
    Args:
        dt (datetime): datetime object for seasonal folder name. If None, use current datetime.
    """
    if dt is None:
        dt = datetime.now()
    seasonal_dir_name = dt.strftime("%Y-%m-%b")
    target_dir = seasonal_dir / seasonal_dir_name
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)

        # populate seasonal dir contents
        seasonal_dev_dir_name = dt.strftime("dev-%b-%Y".lower())
        seasonal_dev_dir = target_dir / seasonal_dev_dir_name
        seasonal_dev_dir.mkdir(parents=True, exist_ok=True)
        create_and_clone_repo(seasonal_dev_dir_name, seasonal_dev_dir, settings.seasonal_dir_template_repo)

        # step 2: clone repo
        # repo = github_client.get_repo("calmmage/seasonal-dir-template")
        # repo.get_contents("/template").download_url

    # step 3: check latest softlink
    latest_seasonal_dir = seasonal_dir / "latest"
    if latest_seasonal_dir.exists():
        latest_seasonal_dir.unlink()
    latest_seasonal_dir.symlink_to(target_dir)

    # todo: link to ~/code dir as well?


# endregion idea 3 - seasonal folder

# region idea 4
# - set up ~/.calmmage dir
# endregion idea 4

# region idea 5 - build zshrc file
# - safe add line to zshrc file
# - safe add variable to zshrc file
# - safe add variable to ~/.env file

# endregion idea 5 - build zshrc file


# region idea 6 - set up ~/code dir - softlinks to key locations
# - main dirs?
# - seasonal (latest, drafts, vscode workspace?)
# - contextst (libs, dev, etc)

# endregion idea 6 - set up ~/code dir - softlinks to key locations
