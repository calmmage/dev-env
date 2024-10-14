import subprocess
from pathlib import Path
import os
import argparse
from git import Repo, GitCommandError
from git.exc import InvalidGitRepositoryError

from dotenv import load_dotenv
from loguru import logger
from tqdm import tqdm

root = Path("/Users/petrlavrov/work/temp/new_meta/")

def clone_or_pull_repo(repo_name: str, target_dir: Path, dry_run: bool):
    repo_path = target_dir / repo_name
    if repo_path.exists():
        try:
            repo = Repo(repo_path)
            if dry_run:
                logger.info(f'[DRY RUN] Would pull latest changes for existing repo {repo_name}')
                current_branch = repo.active_branch.name
                if current_branch != 'main':
                    logger.warning(f'[DRY RUN] Repository {repo_name} is not on the main branch. Current branch: {current_branch}')
            else:
                logger.info(f'Pulling latest changes for existing repo {repo_name}')
                origin = repo.remotes.origin
                origin.pull()
                current_branch = repo.active_branch.name
                if current_branch != 'main':
                    logger.warning(f'Repository {repo_name} is not on the main branch. Current branch: {current_branch}')
        except InvalidGitRepositoryError:
            logger.error(f'Directory {repo_path} exists but is not a valid git repository')
        except Exception as e: 
            logger.error(f'Error processing repository {repo_name}: {e}')
    else:
        if dry_run:
            logger.info(f'[DRY RUN] Would clone repo {repo_name} to {repo_path}')
        else:
            logger.info(f'Cloning repo {repo_name}')
            Repo.clone_from(f'https://github.com/calmmage/{repo_name}.git', repo_path)

def clone_repos(target_dir: Path, dry_run: bool):
    repos_to_clone = [
        'dev-env', 
        # 'calmlib', 'calmmage', 'calmmage-private',
        # 'calmapp', 'personal-website', 'raycast', 'new-bot-lib'
    ]
    
    for repo in tqdm(repos_to_clone, desc="Processing repositories"):
        clone_or_pull_repo(repo, target_dir, dry_run)

def create_poetry_env(dev_env_dir: Path, dry_run: bool):
    if dry_run:
        logger.info(f'[DRY RUN] Would create poetry environment in {dev_env_dir}')
        return "DRY_RUN_POETRY_ENV_PATH"
    else:
        logger.info("Creating poetry environment")
        subprocess.run(['poetry', 'install'], cwd=dev_env_dir, check=True)
        
        # Get the path to the poetry environment
        result = subprocess.run(['poetry', 'env', 'info', '--path'], cwd=dev_env_dir, capture_output=True, text=True, check=True)
        poetry_env_path = result.stdout.strip()
        return poetry_env_path

def set_env_variables(root: Path, poetry_env_path: str, dry_run: bool):
    env_vars = {
        'CALMLIB_ROOT': str(root / 'repos' / 'calmlib'),
        'DEV_ENV_PYTHON_PATH': str(root / 'repos' / 'dev-env'),
        'POETRY_ENV_PATH': poetry_env_path
    }

    env_file_path = root / '.env'
    existing_env_vars = {}

    # Read existing .env file if it exists
    if env_file_path.exists():
        with open(env_file_path, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    existing_env_vars[key] = value

    if dry_run:
        logger.info("[DRY RUN] Would set the following environment variables:")
        for key, value in env_vars.items():
            env_value = os.environ.get(key)
            if env_value:
                if env_value != value:
                    logger.warning(f"[DRY RUN] Environment variable {key} already set with different value: {env_value}")
                else:
                    logger.info(f"[DRY RUN] Environment variable {key} already set with same value: {env_value}")

            if key in existing_env_vars:
                logger.warning(f"[DRY RUN] Variable {key} already in .env file with different value: {existing_env_vars[key]}")
                
            logger.info(f"[DRY RUN] Would write to .env file: {key}={value}")
    else:
        with open(env_file_path, 'w') as f:
            for key, value in env_vars.items():
                # Check if already in environment
                env_value = os.environ.get(key)
                if env_value:
                    if env_value != value:
                        logger.warning(f"Environment variable {key} already set with different value: {env_value}")
                    else:
                        logger.info(f"Environment variable {key} already set with same value: {env_value}")

                # Check if present in the file
                if key in existing_env_vars:
                    logger.warning(f"Variable {key} already in .env file with different value: {existing_env_vars[key]}")
                    
                # Write to .env file
                f.write(f'{key}={value}\n')
        
        logger.info("Environment variables set and saved to .env file")

def create_aliases(root: Path, dry_run: bool):
    aliases = [
        f"alias run-python='poetry run python'",
        f"alias run-script='poetry run python {root}/repos/dev-env/run_script.py'",
        f"alias specific-command='poetry run python {root}/repos/dev-env/specific_command.py'"
    ]
    
    if dry_run:
        logger.info("[DRY RUN] Would create the following aliases:")
        for alias in aliases:
            logger.info(f"[DRY RUN] {alias}")
    else:
        with open(root / '.aliases', 'w') as f:
            for alias in aliases:
                f.write(f'{alias}\n')
        
        logger.info("Aliases created and saved to .aliases file")

def main(dry_run: bool):
    load_dotenv()
    logger.add(root / "setup.log")

    target_dir = root / 'repos'
    if dry_run:
        logger.info(f"[DRY RUN] Would create directory: {target_dir}")
    else:
        target_dir.mkdir(parents=True, exist_ok=True)

    clone_repos(target_dir, dry_run)

    dev_env_dir = target_dir / 'dev-env'
    poetry_env_path = create_poetry_env(dev_env_dir, dry_run)

    set_env_variables(root, poetry_env_path, dry_run)
    create_aliases(root, dry_run)

    if dry_run:
        logger.info("[DRY RUN] Setup simulation completed successfully!")
    else:
        logger.info("Setup completed successfully!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Set up development environment")
    parser.add_argument("--dry-run", action="store_true", help="Simulate the setup process without making changes")
    args = parser.parse_args()

    main(args.dry_run)
