from pathlib import Path
from loguru import logger
from dev_env.core.settings import settings
from dev_env.utils.file_operations import copy_tree, get_backup_path, move_and_symlink
import shutil


def setup_monthly_projects_dir(date=None):
    from datetime import datetime

    if date is None:
        date = datetime.now()
    folder_name = date.strftime("%Y_%m_%b").lower()
    monthly_project_dir = settings.seasonal_projects_dir / folder_name
    if monthly_project_dir.exists():
        logger.warning(f"Monthly project dir already exists: {monthly_project_dir}")
        return monthly_project_dir
    monthly_project_dir.mkdir(parents=True, exist_ok=True)
    paths = ["experiments", "past_refs"]
    for path in paths:
        (monthly_project_dir / path).mkdir(parents=True, exist_ok=True)
    return monthly_project_dir


def setup_new_project_dir(name: str, root: Path = None):
    if root is None:
        root = settings.new_projects_dir
    project_dir = root / name
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


def move_project_to_github(project_path: Path, template_name: str = None, project_name: str = None):
    # Implement the logic to move a project to GitHub
    # This will involve using the GitHub API and git operations
    # For now, we'll just create a placeholder function
    logger.info(f"Moving project {project_path} to GitHub with template {template_name}")
    # Actual implementation would go here


def move_project_to_experiments(project_path: Path, project_name: str = None):
    """
    Move project to calmmage/experiments - assuming its value and intent to preserve it / proceed
    project manager 'move2exp' command
    exp dir path: dev_env.root_dir / "code/structured/dev/calmmage-dev/calmmage/experiments/seasonal/..."
    """
    project_path = Path(project_path)

    if project_name is None:
        project_name = project_path.name
    # target_dir = self.root_dir / "code/structured/dev/calmmage-dev/calmmage/experiments/seasonal"
    target_dir = settings.new_projects_dir
    new_project_path = target_dir / project_name
    shutil.move(str(project_path), str(new_project_path))
    return new_project_path


def move_project_to_beta(project_path: Path, project_name: str = None):
    if project_name is None:
        project_name = project_path.name
    target_dir = settings.root_dir / "code/structured/dev/calmlib-dev/calmlib/beta"
    new_project_path = target_dir / project_name
    shutil.move(str(project_path), str(new_project_path))
    return new_project_path
