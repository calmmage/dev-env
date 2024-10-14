
from dev_env.core.settings import settings


seasonal_dir = settings.root_dir / "seasonal"   
experiments_dir = settings.root_dir / "experiments"
projects_dir = settings.root_dir / "projects"
archive_dir = settings.root_dir / "archive"
contexts_dir = settings.root_dir / "contexts"

all_projects_dirs = [
    seasonal_dir,
    experiments_dir,
    projects_dir,
    archive_dir,
    contexts_dir,
]

