import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from dev.draft.clone_all_projects.clone_all_projects import clone_repos


@pytest.fixture
def mock_repo():
    repo = Mock()
    repo.name = "something-fun"
    repo.full_name = "calmmage/something-fun"
    repo.clone_url = "https://github.com/calmmage/something-fun"
    return repo


@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path / "target_dir"


# @patch("git.Repo.clone_from")
def test_clone_repos(mock_repo, temp_dir):
    repos = [mock_repo]

    stats = clone_repos(repos, temp_dir)

    assert stats == {
        "total": 1,
        "allowed": 1,
        "cloned": 1,
        "skipped": 0,
    }

    expected_clone_path = temp_dir / mock_repo.name
    # mock_clone_from.assert_called_once_with(mock_repo.clone_url, expected_clone_path)

    # Check if the .git directory would exist (we're not actually cloning in the test)
    assert (expected_clone_path / ".git").exists()


# Additional test for skipping existing repos
@patch("git.Repo.clone_from")
def test_clone_repos_skip_existing(mock_clone_from, mock_repo, temp_dir):
    repos = [mock_repo]

    # Create the repo directory to simulate an existing repo
    (temp_dir / mock_repo.name).mkdir(parents=True)

    stats = clone_repos(repos, temp_dir)

    assert stats == {
        "total": 1,
        "allowed": 1,
        "cloned": 0,
        "skipped": 1,
    }

    mock_clone_from.assert_not_called()
