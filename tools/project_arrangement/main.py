from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from config import ProjectArrangerSettings
from loguru import logger
from pydantic import BaseModel
from utils import get_commit_count, get_last_commit_date, is_git_repo


class Project(BaseModel):
    name: str
    path: Path
    github_repo: Optional[str] = None

    @property
    def size(self) -> int:
        total_size = 0
        for file in self.path.rglob("*"):
            # Skip common non-source directories
            if any(
                part in str(file.relative_to(self.path))
                for part in [
                    ".git",
                    ".venv",
                    "venv",
                    "__pycache__",
                    "node_modules",
                    "build",
                    "dist",
                    ".pytest_cache",
                ]
            ):
                continue

            # Only count source code files
            if file.is_file() and file.suffix in [
                ".py",
                ".js",
                ".ts",
                ".jsx",
                ".tsx",
                ".java",
                ".cpp",
                ".c",
                ".h",
                ".hpp",
                ".rs",
                ".go",
                ".rb",
                ".php",
                ".html",
                ".css",
                ".scss",
                ".sql",
                ".sh",
            ]:
                total_size += file.stat().st_size

        return total_size

    @property
    def date(self) -> datetime:
        """
        Essential data when the project was last meaningfully changed.
        """

        # idea 1: if git repo - look at last commit date
        if is_git_repo(self.path):
            return get_last_commit_date(self.path)
        # idea 2: if no git repo - look at file dates
        max_mtime = max(
            file.stat().st_mtime
            for file in self.path.iterdir()
            if file.is_file() and not file.name.startswith(".")
        )
        return datetime.fromtimestamp(max_mtime)


class ProjectArranger:
    def __init__(self, config_path: Path, **kwargs):
        self.settings = ProjectArrangerSettings.from_yaml(config_path, **kwargs)
        # self.projects: List[Project] = []
        self.sorted_projects: Dict[str, List[Project]] = defaultdict(list)

    def build_projects_list(self) -> List[Project]:
        """Discover all projects in configured paths"""
        local_projects = self._build_projets_list_local()
        github_projects = self._build_projets_list_github()
        return self._merge_projects_lists(local_projects, github_projects)

    def _build_projets_list_local(self) -> List[Project]:
        """Discover all projects in local paths"""
        projects = []
        for root in self.settings.root_paths:
            root = root.expanduser()
            if not root.exists():
                logger.warning(f"Path {root} does not exist")
                continue

            for path in root.iterdir():
                if not path.is_dir():
                    continue
                if path.name.startswith("."):
                    continue
                # if path.name in self.settings.ignored_projects:
                #     continue

                projects.append(Project(name=path.name, path=path.resolve()))
        return projects

    def _build_projets_list_github(self) -> List[Project]:
        """Discover all projects in GitHub"""
        return []

    def _merge_projects_lists(
        self, local_projects: List[Project], github_projects: List[Project]
    ) -> List[Project]:
        """Merge projects lists from local and GitHub"""
        # idea: merge projects that have the same github repo
        return local_projects + github_projects

    def sort_projects(self, projects: List[Project]) -> Dict[str, List[Project]]:
        """Sort projects into categories"""
        groups = defaultdict(list)
        for project in projects:
            main_group = self._sort_projects_into_main_groups(project)
            secondary_groups = self._sort_projects_into_secondary_groups(project)

            groups[main_group].append(project)
            for group in secondary_groups:
                groups[group].append(project)
        return groups

    def _sort_projects_into_main_groups(self, project: Project) -> None:
        """Sort projects into main groups"""
        # main groups: experiments, projects, archive and ignored
        # part 1: manually
        main_group = self._sort_main_manual(project)
        if main_group is not None:
            return main_group
        # part 2: automatically
        main_group = self._sort_main_auto(project)
        return main_group

    def _sort_main_manual(self, project: Project) -> Optional[str]:
        """Sort projects into main groups manually"""
        # todo: figure out what to do if local name and github name are different
        if project.name in self.settings.ignore:
            return "ignore"
        elif project.name in self.settings.actual:
            return "projects"
        elif project.name in self.settings.archive:
            return "archive"
        elif project.name in self.settings.experiments:
            return "experiments"
        return None

    def _sort_main_auto(self, project: Project) -> str:
        """Sort projects into main groups automatically. If not specified manually."""
        # idea 1: look at project date
        today = datetime.now()
        if project.date > today - timedelta(days=self.settings.auto_sort_days):
            # look at the size / activity
            if is_git_repo(project.path):
                # look at commit activity
                # - if more than 5 commits in the last 30 days - "actual"
                if (
                    get_commit_count(project.path, days=self.settings.auto_sort_days)
                    > self.settings.auto_sort_commits
                ):
                    return "actual"
            elif project.size > self.settings.auto_sort_size:
                return "actual"
            return "experiments"
        else:
            # look at project size
            if project.size > self.settings.auto_sort_size:
                return "archive"
            return "ignored"

    def _sort_projects_into_secondary_groups(self, project: Project) -> List[str]:
        """Sort projects into secondary groups"""
        # secondary groups: tags and collections.
        # - templates
        # - ai projects
        # ... etc.
        manual_sort = self._sort_secondary_manual(project)
        auto_sort = self._sort_secondary_auto(project)
        return list(set(manual_sort + auto_sort))

    def _sort_secondary_manual(self, project: Project) -> List[str]:
        """Sort projects into secondary groups manually
        Returns list of tags/collections the project should be sorted into."""
        res = []
        if project.name in self.settings.cool:
            res.append("cool")
        if project.name in self.settings.templates:
            res.append("templates")
        return res

    def _sort_secondary_auto(self, project: Project) -> List[str]:
        """Sort projects into secondary groups automatically. If not specified manually.
        Returns list of tags/collections the project should be sorted into."""
        res = []
        if "template" in project.name.lower():
            res.append("templates")
        return res

    def print_results(self) -> None:
        """Print sorted projects"""
        print("\nProject Groups:")
        for group, proj_list in self.sorted_projects.items():
            print(f"\n{group.title()}:")
            for proj in sorted(proj_list, key=lambda x: x.name):
                print(f"- {proj.name}")
