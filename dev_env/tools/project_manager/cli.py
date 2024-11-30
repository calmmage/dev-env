from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from rich.console import Console

from dev_env.tools.project_manager.src.main import ProjectManager

app = typer.Typer()
console = Console()

DEFAULT_CONFIG = Path(__file__).parent / "config.yaml"


@app.command()
def new_project(
    name: str,
    description: Optional[str] = None,
    private: bool = False,
    config: Path = DEFAULT_CONFIG,
):
    """Create a new project"""
    manager = ProjectManager(config)
    manager.create_project(name, description, private)


@app.command()
def new_mini_project(
    name: str,
    description: Optional[str] = None,
    private: bool = True,
    config: Path = DEFAULT_CONFIG,
):
    """Create a new mini-project"""
    manager = ProjectManager(config)
    manager.create_mini_project(name, description, private)


@app.command()
def new_todo(
    name: Optional[str] = None,
    project: Optional[str] = None,
    config: Path = DEFAULT_CONFIG,
):
    """Create a new todo file"""
    manager = ProjectManager(config)
    manager.create_todo(name, project)


@app.command()
def new_feature(
    name: str,
    description: Optional[str] = None,
    project: Optional[str] = None,
    config: Path = DEFAULT_CONFIG,
):
    """Create a new feature draft"""
    manager = ProjectManager(config)
    manager.create_feature(name, description, project)


if __name__ == "__main__":
    app()
