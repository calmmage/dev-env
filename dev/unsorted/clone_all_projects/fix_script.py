import os
import shutil
from pathlib import Path
from loguru import logger


def fix_cloned_repos(target_dir, dry_run=False):
    target_dir = Path(target_dir)
    fixed_count = 0
    skipped_count = 0
    to_remove_dir = target_dir / "to_remove"
    to_remove_dir.mkdir(exist_ok=True)

    for repo_dir in target_dir.iterdir():
        if not repo_dir.is_dir():
            continue

        nested_repo_dir = repo_dir / repo_dir.name

        if nested_repo_dir.exists() and (nested_repo_dir / ".git").exists():
            logger.info(f"{'[DRY RUN] Would fix' if dry_run else 'Fixing'} incorrectly cloned repo: {repo_dir.name}")

            # 1. Move repo -> temp.repo
            temp_dir = repo_dir.with_name(f"temp.{repo_dir.name}")
            logger.debug(f"Moving {repo_dir} to {temp_dir}")
            if not dry_run:
                repo_dir.rename(temp_dir)

            nested_repo_dir = temp_dir / repo_dir.name
            # 2. Move temp.repo/repo -> repo
            logger.debug(f"Moving {nested_repo_dir} to {repo_dir}")
            if not dry_run:
                nested_repo_dir.rename(repo_dir)

            # 3. Remove temp.repo
            # logger.debug(f"Removing {temp_dir}")
            logger.debug(f"Moving {temp_dir} to {to_remove_dir / repo_dir.name}")
            if not dry_run:
                # shutil.rmtree(temp_dir)
                temp_dir.rename(to_remove_dir / repo_dir.name)

            fixed_count += 1
        else:
            logger.info(f"Repo structure looks correct: {repo_dir.name}")
            skipped_count += 1

    return fixed_count, skipped_count


if __name__ == "__main__":
    target_dir = Path("~/work/projects").expanduser()

    dry_run = False
    # dry_run = True
    fixed_count, skipped_count = fix_cloned_repos(target_dir, dry_run=dry_run)
    print(f"{'[DRY RUN] Would fix' if dry_run else 'Fixed'} {fixed_count} incorrectly cloned repositories.")
    print(f"Skipped {skipped_count} repositories with correct structure.")
