#!/usr/bin/env python3
"""Standalone script to manage dev-env repository location and updates"""

import sys
import os
from pathlib import Path
from subprocess import run, check_output
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_dev_env_path():
    """Get dev-env path by sourcing ~/.dev-env-location"""
    location_file = Path.home() / '.dev-env-location'
    if not location_file.exists():
        raise RuntimeError("Dev-env location not configured. Please run bootstrap.sh first")
    
    # Source the file and get the environment variable
    cmd = f'source {location_file} && echo $DEV_ENV_PATH'
    try:
        dev_env_path = check_output(['bash', '-c', cmd], text=True).strip()
        return Path(dev_env_path)
    except Exception as e:
        logger.error(f"Failed to source .dev-env-location: {e}")
        raise

def git_pull_with_fetch(repo_path):
    """Simple git operations using subprocess"""
    logger.info(f"Updating repo at {repo_path}")
    try:
        run(['git', 'fetch', '--all'], cwd=repo_path, check=True)
        run(['git', 'pull'], cwd=repo_path, check=True)
        return True
    except Exception as e:
        logger.error(f"Failed to update repository: {e}")
        return False

def clone_or_update_dev_env():
    """Main function to manage dev-env repo"""
    try:
        dev_env_path = get_dev_env_path()
        if dev_env_path.exists():
            logger.info("Updating existing dev-env repository")
            success = git_pull_with_fetch(dev_env_path)
            if success:
                logger.info("Dev-env repository updated successfully")
            else:
                sys.exit(1)
        else:
            logger.info(f"Cloning dev-env repository to {dev_env_path}")
            dev_env_path.parent.mkdir(parents=True, exist_ok=True)
            run(['git', 'clone', 'https://github.com/calmmage/dev-env.git', 
                 str(dev_env_path)], check=True)
            logger.info("Dev-env repository cloned successfully")
    except Exception as e:
        logger.error(f"Error managing dev-env repository: {e}")
        sys.exit(1)

if __name__ == '__main__':
    clone_or_update_dev_env()