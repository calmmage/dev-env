from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from functools import cached_property
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger
from pydantic import BaseModel

from dev.draft.project_management_v2.project_organization.old.config import ProjectArrangerSettings
from dev.draft.project_management_v2.project_organization.old.utils import (
    get_commit_count,
    get_first_commit_date,
    get_last_commit_date,
    is_git_repo,
)


# todo: use everywhere?
class Group(str, Enum):
    experiments = "experiments"
    projects = "projects"  # rename to actual? - but folder stays as projects/
    unsorted = "unsorted"
    archive = "archive"
    ignore = "ignore"


class Project(BaseModel):
    name: str
    path: Path
    github_repo: Optional[str] = None

    # todo: use external ignore rules
    #  option 1: gitignore
    __ignored_paths = [
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        "build",
        "dist",
        ".pytest_cache",
    ]

    __source_extensions = [
        ".py",
        ".md",
        # ".js",
        # ".ts",
        # ".jsx",
        # ".tsx",
        # ".java",
        ".cpp",
        # ".c",
        # ".h",
        # ".hpp",
        # ".rs",
        # ".go",
        # ".rb",
        # ".php",
        # ".html",
        # ".css",
        # ".scss",
        # ".sql",
        ".sh",
    ]

    @cached_property
    def size(self) -> int:
        total_size = 0
        for file in self.path.rglob("*"):
            # Skip common non-source directories
            if any(part in str(file.relative_to(self.path)) for part in self.__ignored_paths):
                continue

            # Only count source code files
            if file.is_file() and file.suffix in self.__source_extensions:
                total_size += file.stat().st_size
        return total_size

    FORMAT_MODE: int = 2

    # todo: show main language?
    @property
    def size_formatted(self) -> str:
        """Format size with appropriate units and alignment"""
        if self.FORMAT_MODE == 1:
            if self.size >= 1_000_000:  # 1M+
                return f"{self.size/1_000_000:>8.2f}M"
            elif self.size >= 1_000:  # 1K+
                return f"{self.size/1_000:>8.2f}K"
            else:
                return f"{self.size:>8}B"
        elif self.FORMAT_MODE == 2:
            # Round to 3 significant digits and add commas
            if self.size >= 1000:
                magnitude = len(str(self.size)) - 3
                rounded = (self.size // (10**magnitude)) * (10**magnitude)
                return f"{rounded:>10,}"
            return f"{self.size:>10}"

    @cached_property
    def date(self) -> datetime:
        """
        Essential data when the project was last meaningfully changed.
        """
        # idea 1: if git repo - look at last commit date
        if is_git_repo(self.path):
            try:
                return get_last_commit_date(self.path)
            except ValueError:
                pass
        # idea 2: if no git repo - look at file dates
        paths = list(self.path.iterdir())
        paths.append(self.path)
        max_mtime = max(file.stat().st_mtime for file in paths if not file.name.startswith("."))
        return datetime.fromtimestamp(max_mtime)

    @cached_property
    def created_date(self) -> datetime:
        """
        Essential data when the project was created.
        """
        # idea 1: if git repo - look at first commit date
        if is_git_repo(self.path):
            try:
                return get_first_commit_date(self.path)
            except ValueError:
                pass
        # idea 2: if no git repo - look at file dates
        paths = list(self.path.iterdir())
        paths.append(self.path)
        min_mtime = min(file.stat().st_mtime for file in paths if not file.name.startswith("."))
        return datetime.fromtimestamp(min_mtime)

    @cached_property
    def current_group(self) -> str:
        if self.path is None:
            return Group.ignore
        group = self.path.parent.name
        if group not in Group.__members__:
            logger.warning(f"Unknown group {group}")
            return Group.unsorted
        return Group(group)


class ProjectArranger:
    def __init__(self, config_path: Path, **kwargs):
        self.settings = ProjectArrangerSettings.from_yaml(config_path, **kwargs)

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

    def get_current_groups(self, projects: List[Project]) -> Dict[str, Dict[str, List[Project]]]:
        """Build groups dictionary based on current filesystem structure"""
        groups = {"main": defaultdict(list), "secondary": defaultdict(list)}

        # Sort into main groups based on current directory structure
        for project in projects:
            current_group = project.current_group
            groups["main"][current_group].append(project)

        # TODO: Implement secondary groups scanning
        # Will need to:
        # 1. Scan additional folders like 'templates/', 'ai-projects/', etc.
        # 2. Add a method to detect current secondary groups for a project
        # 3. Update Project class to support multiple current groups

        return groups

    def sort_projects(self, projects: List[Project]) -> Dict[str, Dict[str, List[Project]]]:
        """Sort projects into target categories based on config"""
        groups = {"main": defaultdict(list), "secondary": defaultdict(list)}
        for project in projects:
            main_group = self._sort_projects_into_main_groups(project)
            secondary_groups = self._sort_projects_into_secondary_groups(project)

            groups["main"][main_group].append(project)
            for group in secondary_groups:
                groups["secondary"][group].append(project)
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
                    return "projects"  # "actual"
            elif project.size > self.settings.auto_sort_size:
                return "projects"  # "actual"
            return "experiments"
        else:
            # look at project size
            if project.size > self.settings.auto_sort_size:
                return "archive"
            return "ignore"

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

    @staticmethod
    def print_all_results(groups, print_sizes: bool = False) -> None:
        """Print all projects in their groups"""
        print("Main Project Groups:")
        for group in Group.__members__:
            proj_list = groups["main"][group]
            print(f"{group.title()} ({len(proj_list)}):")
            for proj in sorted(proj_list, key=lambda x: x.name):
                size_str = f"[{proj.size_formatted}] " if print_sizes else ""
                print(f"- {size_str}{proj.name}")
            print()

        print("\n" + "=" * 50 + "\n")

        print("Secondary Project Groups:")
        for group, proj_list in sorted(groups["secondary"].items()):
            print(f"{group.title()} ({len(proj_list)}):")
            for proj in sorted(proj_list, key=lambda x: x.name):
                size_str = f"[{proj.size_formatted}] " if print_sizes else ""
                print(f"- {size_str}{proj.name}")
            print()

    @staticmethod
    def print_changes(old_groups, new_groups, print_sizes: bool = False) -> None:
        """Print only the changes between old and new groups"""
        # Compare main groups
        print("Changes in Main Project Groups:")
        for group in Group.__members__:
            old_projects = {p.name for p in old_groups["main"].get(group, [])}
            new_projects = {p.name for p in new_groups["main"].get(group, [])}

            added = new_projects - old_projects
            removed = old_projects - new_projects

            if added or removed:
                print(f"\n{group.title()}:")
                if added:
                    print("  Added:")
                    for proj_name in sorted(added):
                        proj = next(p for p in new_groups["main"][group] if p.name == proj_name)
                        size_str = f"[{proj.size_formatted}] " if print_sizes else ""
                        print(f"  + {size_str}{proj_name}")
                if removed:
                    print("  Removed:")
                    for proj_name in sorted(removed):
                        print(f"  - {proj_name}")

        # Compare secondary groups
        if any(old_groups["secondary"]) or any(new_groups["secondary"]):
            print("\nChanges in Secondary Project Groups:")
            for group in set(old_groups["secondary"].keys()) | set(new_groups["secondary"].keys()):
                old_projects = {p.name for p in old_groups["secondary"].get(group, [])}
                new_projects = {p.name for p in new_groups["secondary"].get(group, [])}

                added = new_projects - old_projects
                removed = old_projects - new_projects

                if added or removed:
                    print(f"\n{group.title()}:")
                    if added:
                        print("  Added:")
                        for proj_name in sorted(added):
                            proj = next(
                                p for p in new_groups["secondary"][group] if p.name == proj_name
                            )
                            size_str = f"[{proj.size_formatted}] " if print_sizes else ""
                            print(f"  + {size_str}{proj_name}")
                    if removed:
                        print("  Removed:")
                        for proj_name in sorted(removed):
                            print(f"  - {proj_name}")
