from pathlib import Path
from dev_env.core.settings import settings
from dev_env.utils.project_operations import setup_monthly_projects_dir


# from dev_env.utils.file_operations import copy_tree


def monthly_job():
    projects_dir = setup_monthly_projects_dir()

    # Link seasonal folder to the 'latest'
    source = projects_dir
    target = settings.seasonal_projects_dir / "latest"
    if target.is_symlink():
        target.unlink()
    target.symlink_to(source)

    # Link "playground" to the latest/experiments
    source = target / "experiments"
    target = settings.root_dir / "playground"
    if target.is_symlink():
        target.unlink()
    target.symlink_to(source)


def daily_job():
    projects_dir = settings.seasonal_projects_dir / "latest"
    target_dir = settings.project_unsorted_dir
    for project_dir in projects_dir.iterdir():
        if project_dir.name in ["experiments", "past_refs"]:
            continue
        if project_dir.is_dir():
            target_path = target_dir / project_dir.name
            if not target_path.exists():
                target_path.symlink_to(project_dir)
