from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from config import ProjectArrangerSettings
from loguru import logger
from pydantic import BaseModel


class Project(BaseModel):
    name: str
    path: Path

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


class ProjectArranger:
    def __init__(self, config_path: Path, **kwargs):
        self.settings = ProjectArrangerSettings.from_yaml(config_path, **kwargs)
        self.projects: List[Project] = []
        self.sorted_projects: Dict[str, List[Project]] = defaultdict(list)

    def build_projects_list(self) -> None:
        """Discover all projects in configured paths"""
        local_projects = self._build_projets_list_local()
        github_projects = self._build_projets_list_github()
        self._merge_projects_lists(local_projects, github_projects)

    def _build_projets_list_local(self) -> None:
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

    def _build_projets_list_github(self) -> None:
        """Discover all projects in GitHub"""
        return []

    def _merge_projects_lists(
        self, local_projects: List[Project], github_projects: List[Project]
    ) -> None:
        """Merge projects lists from local and GitHub"""
        # idea: merge projects that have the same github repo
        return local_projects + github_projects

    def sort_projects(self) -> None:
        """Sort projects into categories"""
        for project in self.projects:
            main_group = self._sort_projects_into_main_groups(project)
            secondary_groups = self._sort_projects_into_secondary_groups(project)
            self.sorted_projects[main_group].append(project)
            for group in secondary_groups:
                self.sorted_projects[group].append(project)

    def _sort_projects_into_main_groups(self, project: Project) -> None:
        """Sort projects into main groups"""
        # main groups: experiments, projects, archive and ignored
        # part 1: manually
        if project.name in self.settings.ignored_projects:
            return "ignore"
        elif project.name in self.settings.main_projects:
            return "projects"
        elif "experiments" in str(project.path):
            return "experiments"
        elif "archive" in str(project.path):
            return "archive"
        else:
            return "unsorted"

    def _sort_main_manual(self, project: Project) -> None:
        """Sort projects into main groups manually"""
        pass

    def _sort_main_auto(self, project: Project) -> None:
        """Sort projects into main groups automatically. If not specified manually."""

        pass

    def _sort_projects_into_secondary_groups(self, project: Project) -> None:
        """Sort projects into secondary groups"""
        # secondary groups: tags and collections.
        # - templates
        # - ai projects
        # ... etc.
        manual_sort = self._sort_secondary_manual(project)
        auto_sort = self._sort_secondary_auto(project)
        return set(manual_sort + auto_sort)

    def _sort_secondary_manual(self, project: Project) -> None:
        """Sort projects into secondary groups manually
        Returns list of tags/collections the project should be sorted into."""

        return []

    def _sort_secondary_auto(self, project: Project) -> None:
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
