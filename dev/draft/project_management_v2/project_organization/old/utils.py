from datetime import datetime, timedelta
from pathlib import Path

from git import GitCommandError, Repo


def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


# todo: update as below
def get_last_commit_date(path: Path) -> datetime:
    repo = Repo(path)
    return datetime.fromtimestamp(repo.head.commit.committed_date)


def get_first_commit_date(path: Path) -> datetime:
    """
    Retrieves the date of the first commit in the Git repository at the given path.

    Args:
        path (Path): The filesystem path to the Git repository.

    Returns:
        datetime: The datetime of the first commit.

    Raises:
        ValueError: If the repository has no commits.
        GitCommandError: If the provided path is not a valid Git repository.
    """
    try:
        repo = Repo(path)
    except GitCommandError as e:
        raise ValueError(f"The path '{path}' is not a valid Git repository.") from e

    if repo.bare:
        raise ValueError(f"The repository at '{path}' is bare and has no commits.")

    try:
        # Attempt to iterate commits in reverse (from oldest to newest)
        first_commit = next(repo.iter_commits(reverse=True))
    except StopIteration:
        raise ValueError("No commits found in the repository.")

    return first_commit.committed_datetime


def get_commit_count(path: Path, days: int = 30) -> int:
    repo = Repo(path)
    since_date = datetime.now() - timedelta(days=days)
    return len(list(repo.iter_commits(since=since_date)))
