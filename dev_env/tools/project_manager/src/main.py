import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import git
from loguru import logger

from dev_env.lib.project_utils import ProjectDiscovery
from dev_env.tools.project_manager.src.config import ProjectManagerConfig


class ProjectManager:
    def __init__(self, config_path: Path):
        """Initialize Project Manager with configuration"""
        self.config = ProjectManagerConfig.from_yaml(config_path)
        self.discovery = ProjectDiscovery()
        self._github_token = None
        self._github_client = None
        self._templates = None

    @property
    def github_token(self) -> str:
        """Get GitHub token from environment variables"""
        if self._github_token is None:
            # Try to load from ~/.env first, then system env vars
            env_path = Path.home() / ".env"
            if env_path.exists():
                from dotenv import load_dotenv

                load_dotenv(env_path)

            token = os.getenv("GITHUB_API_TOKEN")
            if token is None:
                raise ValueError(
                    "Missing GitHub API token. "
                    "Please add it to ~/.env or system environment variables. "
                )
            self._github_token = token
        return self._github_token

    @property
    def github_client(self):
        """Get GitHub client instance"""
        if self._github_client is None:
            from github import Github

            self._github_client = Github(self.github_token)
        return self._github_client

    def get_templates(self, reset_cache=False):
        """Get all available GitHub templates"""
        if self._templates is None or reset_cache:
            repos = self.github_client.get_user().get_repos()
            self._templates = {repo.name: repo for repo in repos if repo.is_template}
        return self._templates

    def _create_repo_from_template(self, name: str, template_name: str) -> str:
        """Create a new GitHub repository from template"""
        logger.debug(f"Creating repository {name} from template: {template_name}")

        github_client = self.github_client
        username = github_client.get_user().login

        # Validate template
        templates = self.get_templates()
        if template_name not in templates:
            raise ValueError(
                f"Invalid template: {template_name}. Available: {list(templates.keys())}"
            )

        # Check if repo exists
        if name in [repo.name for repo in github_client.get_user().get_repos()]:
            raise ValueError(f"Repository already exists: https://github.com/{username}/{name}")

        # Create repo from template
        github_client._Github__requester.requestJsonAndCheck(
            "POST",
            f"/repos/{username}/{template_name}/generate",
            input={"owner": username, "name": name},
        )

        url = f"https://github.com/{username}/{name}"
        logger.debug(f"Repository created: {url}")
        return url

    def _clone_github_repository(
        self, name: str, project_dir: Path, retries: int = 3, retry_delay: int = 5
    ):
        """Clone GitHub repository to local directory"""
        project_dir = Path(project_dir)
        username = self.github_client.get_user().login
        url = f"https://{self.github_token}@github.com/{username}/{name}.git"

        if project_dir.exists() and list(project_dir.iterdir()):
            raise ValueError(f"Project directory not empty: {project_dir}")

        for i in range(retries):
            try:
                repo = git.Repo.clone_from(url, str(project_dir))
                repo.git.pull()

                # Verify clone success
                if not (project_dir / ".git").exists():
                    raise ValueError("Git directory not found")

                logger.debug(f"Repository cloned successfully to {project_dir}")
                return project_dir

            except Exception as e:
                logger.warning(f"Clone attempt {i+1} failed: {e}")
                if i < retries - 1:
                    import time

                    time.sleep(retry_delay)
                    continue
                raise

    def _prompt_project_name(self) -> str:
        """Prompt user for project purpose and generate name"""
        response = input("What do you want to do?\n")
        # For now return as is, later we'll add AI name generation
        return response

    def _validate_name_with_ai(self, name: str) -> tuple[bool, Optional[str]]:
        """Validate name with AI and optionally get suggestion"""
        # TODO: Implement actual AI validation using query_gpt
        # prompt = f"""Is '{name}' a good project name? Consider:
        # - Clarity and descriptiveness
        # - Length (should be concise)
        # - Standard naming conventions
        #
        # Return format:
        # VALID: true/false
        # SUGGESTION: better_name (only if VALID is false)
        # """
        # Placeholder implementation
        return True, None

    def _check_github_conflicts(self, name: str) -> bool:
        """Check if name conflicts with existing GitHub repos"""
        # TODO: Implement GitHub API check
        return False

    def create_project(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        private: bool = False,
        template: str = "python-project-template",
    ):
        """Create a new project in experiments using GitHub template.

        Args:
            name: Project name. If None, will prompt user
            description: Project description/purpose
            private: Whether to create as private repository
            template: GitHub template name to use
        """
        # 1. Name Processing
        if name is None:
            name = self._prompt_project_name()

        # Validate with AI
        is_valid, suggestion = self._validate_name_with_ai(name)
        if not is_valid:
            logger.warning(f"AI suggests better name: {suggestion}")
            name = suggestion

        # Check GitHub conflicts
        if self._check_github_conflicts(name):
            raise ValueError(f"Project name '{name}' conflicts with existing GitHub repository")

        # 2. Project Creation
        try:
            # Create repo from template
            self._create_repo_from_template(name, template)

            # Clone to local directory
            experiments_dir = Path(self.config.targets["new_project"].destination)
            project_dir = experiments_dir / name
            self._clone_github_repository(name, project_dir)

        except Exception as e:
            logger.error(f"Failed to create GitHub project: {e}")
            raise

        logger.info(f"Project '{name}' created successfully at {project_dir}")
        return project_dir

    def create_mini_project(
        self, name: str, description: Optional[str] = None, private: bool = True
    ):
        """Create a new mini-project in calmmage or calmmage-private"""
        logger.info(f"Creating new mini-project: {name}")
        raise NotImplementedError()

    def create_todo(self, name: Optional[str] = None, project: Optional[str] = None):
        """Create a new todo file"""
        if project is None:
            project = self.discovery.get_current_project()

        if name is None:
            name = datetime.now().strftime(self.config.settings.todo_format)

        logger.info(f"Creating new todo in {project}: {name}")
        raise NotImplementedError()

    def create_feature(
        self, name: str, description: Optional[str] = None, project: Optional[str] = None
    ):
        """Create a new feature draft"""
        if project is None:
            project = self.discovery.get_current_project()

        logger.info(f"Creating new feature in {project}: {name}")
        raise NotImplementedError()
