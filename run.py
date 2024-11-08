"""
This script deploys calmmage dev environment
"""

import typer
from loguru import logger

from dev_env.setup.setup_shell_profiles_and_env import clone_or_update_dev_env, update_shell_profiles

app = typer.Typer()


@app.command()
def main():
    """
    Deploy calmmage dev environment
    """
    logger.info("Starting dev environment setup")

    # Step 1: Clone or update dev_env repository
    clone_or_update_dev_env()

    # Step 2: Update .zshrc
    update_shell_profiles()

    logger.success("Dev environment setup complete")
    logger.info("Please restart your terminal or run 'source ~/.zshrc' to apply changes")


if __name__ == "__main__":
    app()
