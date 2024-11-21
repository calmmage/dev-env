from datetime import datetime, timedelta
from pathlib import Path

from git import Repo


def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


def get_last_commit_date(path: Path) -> datetime:
    repo = Repo(path)
    return datetime.fromtimestamp(repo.head.commit.committed_date)


def get_commit_count(path: Path, days: int = 30) -> int:
    repo = Repo(path)
    since_date = datetime.now() - timedelta(days=days)
    return len(list(repo.iter_commits(since=since_date)))
