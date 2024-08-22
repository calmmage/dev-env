import shutil
from pathlib import Path

from loguru import logger


def is_git_repo(path):
    return (path / ".git").is_dir()


def fix_cloned_repos(target_dir, dry_run=False):
    target_dir = Path(target_dir)
    fixed_count = 0
    skipped_count = 0

    for repo_dir in target_dir.iterdir():
        if not repo_dir.is_dir():
            continue

        nested_repo_dir = repo_dir / repo_dir.name
        if nested_repo_dir.exists() and is_git_repo(nested_repo_dir):
            if is_git_repo(repo_dir):
                logger.info(f"Skipping {repo_dir.name}: Both parent and nested dirs are git repos")
                skipped_count += 1
                continue

            logger.info(f"Fixing incorrectly cloned repo: {repo_dir.name}")

            if not dry_run:
                # Move contents of nested directory to parent
                for item in nested_repo_dir.iterdir():
                    if item.name != repo_dir.name:  # Avoid recursive copy
                        dest = repo_dir / item.name
                        if dest.exists():
                            logger.warning(f"Skipping {item.name}: Already exists in parent")
                        else:
                            shutil.move(str(item), str(repo_dir))

                # Remove empty nested directory
                if not any(nested_repo_dir.iterdir()):
                    nested_repo_dir.rmdir()
                else:
                    logger.warning(f"Nested dir not empty after move: {nested_repo_dir}")

            fixed_count += 1
        elif is_git_repo(repo_dir):
            logger.info(f"Repo already correctly cloned: {repo_dir.name}")
        else:
            logger.warning(f"Unexpected directory structure: {repo_dir.name}")

    return fixed_count, skipped_count


if __name__ == "__main__":
    target_dir = Path("~/work/projects").expanduser()

    # dry_run = False
    dry_run = True
    fixed_count, skipped_count = fix_cloned_repos(target_dir, dry_run=dry_run)
    print(f"Fixed {fixed_count} incorrectly cloned repositories.")
    print(f"Skipped {skipped_count} repositories with intentional nested structure.")
