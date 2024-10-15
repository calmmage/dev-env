import pytest
from pathlib import Path
from github import Github
from dev_env.core.git_utils import get_repo
from dev_env.core.settings import settings


@pytest.fixture(scope="module")
def github_client():
    return Github(settings.github_api_token.get_secret_value())


@pytest.fixture(scope="module")
def all_repos(github_client):
    return list(github_client.get_user().get_repos())


def test_get_repo_by_short_name(github_client, all_repos):
    repo = get_repo("calmmage-private")
    assert repo is not None
    assert repo.name == "calmmage-private"
    assert repo.full_name == "calmmage/calmmage-private"


def test_get_repo_by_full_name(github_client, all_repos):
    repo = get_repo("calmmage/calmmage-private")
    assert repo is not None
    assert repo.name == "calmmage-private"
    assert repo.full_name == "calmmage/calmmage-private"


def test_get_repo_by_url(github_client, all_repos):
    repo = get_repo("https://github.com/calmmage/calmmage-private.git")
    assert repo is not None
    assert repo.name == "calmmage-private"
    assert repo.full_name == "calmmage/calmmage-private"


def test_get_repo_nonexistent(github_client, all_repos):
    repo = get_repo("nonexistent-repo")
    assert repo is None
