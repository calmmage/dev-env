from dev_env.dev_env import CalmmageDevEnv, logger
import git
from dotenv import load_dotenv
from loguru import logger
from pathlib import Path
from tqdm.auto import tqdm

import dev_env.core.git_utils

load_dotenv()

allowed_teams = ["calmmage", "Augmented-development", "engineering-friends", "lavrpetrov"]


def clone_repos(repos, target_dir):
    stats = {
        "total": len(repos),
        "allowed": 0,
        "cloned": 0,
        "skipped": 0,
    }

    for repo in tqdm(repos):
        full_repo_name = repo.full_name
        if not any([full_repo_name.startswith(team) for team in allowed_teams]):
            logger.info(f"Skipping {full_repo_name}")
            continue
        stats["allowed"] += 1

        target_path = Path(target_dir) / repo.name
        if not target_path.exists():
            git.Repo.clone_from(repo.clone_url, target_path)
            stats["cloned"] += 1
        else:
            stats["skipped"] += 1

    return stats


if __name__ == "__main__":
    dev_env = CalmmageDevEnv()
    target_dir = dev_env.all_projects_dir

    # get all my projects
    my_repos = list(dev_env.core.git_utils.github_client.get_user().get_repos())

    stats = clone_repos(my_repos, target_dir)
    print(stats)
