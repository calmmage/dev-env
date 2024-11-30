from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger
from pydantic import BaseModel

from dev_env.lib.project_utils import ProjectDiscovery
from dev_env.tools.project_manager.src.config import ProjectManagerConfig


class ProjectManager:
    def __init__(self, config_path: Path):
        self.config = ProjectManagerConfig.from_yaml(config_path)
        self.discovery = ProjectDiscovery()

    def create_project(self, name: str, description: Optional[str] = None, private: bool = False):
        """Create a new project in experiments"""
        # Implementation will go here
        logger.info(f"Creating new project: {name}")
        raise NotImplementedError()

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
