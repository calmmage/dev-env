import os
import shutil
from pathlib import Path
from loguru import logger


def fix_cloned_repos(target_dir, dry_run=False):
    target_dir = Path(target_dir)
    fixed_count = 0

    for repo_dir in target_dir.iterdir():
        if not repo_dir.is_dir():
            continue

        nested_repo_dir = repo_dir / repo_dir.name
        if nested_repo_dir.exists() and (nested_repo_dir / ".git").exists():
            logger.info(f"Fixing incorrectly cloned repo: {repo_dir.name}")

            if not dry_run:
                # Move contents of nested directory to parent
                for item in nested_repo_dir.iterdir():
                    shutil.move(str(item), str(repo_dir))

                # Remove empty nested directory
                nested_repo_dir.rmdir()

            fixed_count += 1
        elif (repo_dir / ".git").exists():
            logger.info(f"Repo already correctly cloned: {repo_dir.name}")
        else:
            logger.warning(f"Unexpected directory structure: {repo_dir.name}")

    return fixed_count


if __name__ == "__main__":

    target_dir = Path("~/work/projects").expanduser()
    #
    # import sys
    #
    # if len(sys.argv) != 2:
    #     print("Usage: python fix_cloned_repos.py <target_directory>")
    #     sys.exit(1)
    #
    # target_dir = sys.argv[1]
    # dry_run = False
    dry_run = True
    fixed_count = fix_cloned_repos(target_dir, dry_run=dry_run)
    print(f"Fixed {fixed_count} incorrectly cloned repositories.")
