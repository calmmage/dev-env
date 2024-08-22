from dev_env.dev_env import CalmmageDevEnv, logger
import git
from dotenv import load_dotenv
from loguru import logger
load_dotenv()

# clone all my projects

# use github python api to clone all my projects
# add to python dependencies..
# list all projects

# there's github token in .env

#
from tqdm.auto import tqdm
allowed_teams=["calmmage", "Augmented-development", "engineering-friends", "lavrpetrov"]


if __name__ == '__main__':

    dev_env = CalmmageDevEnv()
    target_dir = dev_env.all_projects_dir
    raise Exception("This is a broken script - fix first! Copies repos into repo/repo folder")

    # get all my projects
    my_repos = list(dev_env.github_client.get_user().get_repos())
    stats = {
        "total": len(my_repos),
        "allowed": 0,
        "cloned": 0,
        "skipped": 0,


    }
    for repo in tqdm(my_repos):
        full_repo_name = repo.full_name
        if not any([full_repo_name.startswith(team) for team in allowed_teams]):
            logger.info(f"Skipping {full_repo_name}")
            continue
        stats["allowed"] += 1
        # print(full_repo_name)
        # git.Repo.clone_from(repo.clone_url, dev_env.root_dir / repo.name)
        target_path = target_dir / repo.name
        if not target_path.exists():
            git.Repo.clone_from(repo.clone_url, target_path / repo.name)
            stats["cloned"] += 1
        else:
            stats["skipped"] += 1

    # print("repos", list( dev_env.github_client.get_repos()))
    print(stats)