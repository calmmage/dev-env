from loguru import logger
from pydantic_settings import BaseSettings

from dev_env.core.git_utils import get_github_client


class Settings(BaseSettings):
    github_api_token: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def list_all_repos(github_client):
    """List all repositories the authenticated user has access to."""
    user = github_client.get_user()
    logger.info(f"Authenticated as: {user.login}")

    repos = list(user.get_repos())
    logger.info(f"Found {len(repos)} repositories")
    return repos


def add_secret_to_repo(repo, secret_name: str, secret_value: str):
    """Add a secret to a specific repository."""
    try:
        # Create or update secret - using correct parameter order
        repo.create_secret(
            secret_name,
            secret_value,
            # secret_type="actions" is default, no need to specify
        )
        logger.success(f"Successfully added secret {secret_name} to {repo.full_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to add secret to {repo.full_name}: {e}")
        return False


def main(secret_name: str, secret_value: str):
    github_client = get_github_client()
    repos = list_all_repos(github_client)

    success_count = 0
    fail_count = 0

    for repo in repos:
        if add_secret_to_repo(repo, secret_name, secret_value):
            success_count += 1
        else:
            fail_count += 1

    logger.info(f"Operation completed. Success: {success_count}, Failed: {fail_count}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add a secret to all GitHub repositories")
    parser.add_argument("secret_name", help="Name of the secret to add")
    parser.add_argument("secret_value", help="Value of the secret")

    args = parser.parse_args()
    main(args.secret_name, args.secret_value)
