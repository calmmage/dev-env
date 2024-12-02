from pathlib import Path
from typing import List, Optional

from loguru import logger

from dev_env.core.pm_utils.destinations import DestinationsRegistry
from dev_env.tools.project_discoverer.pd_config import ProjectDiscovererConfig


class ProjectDiscoverer:
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).parent / "pd_config.yaml"
        self.config = ProjectDiscovererConfig.from_yaml(config_path)
        self.dr = DestinationsRegistry()

    def quick_search(self, query: str) -> List[Path]:
        """Search for projects in common project directories"""
        results = []

        for dest in self.dr.destinations.values():
            if not dest.path.exists():
                continue

            # Get patterns based on destination type
            if dest.name in self.config.seasonal_destinations:
                search_patterns = self.config.seasonal_patterns
            elif dest.name == "examples":
                search_patterns = self.config.glob_patterns["examples"]
            else:
                # todo: check this works fine
                search_patterns = self.config.glob_patterns.get(dest.type.value, [])

            # Search using glob patterns
            for pattern in search_patterns:
                results.extend(
                    p
                    for p in dest.path.glob(pattern)
                    if p.is_dir() and query.lower() in p.name.lower()
                )

        return sorted(results)

    def get_outer_project_dirs(self, path):
        """
        Find all project directories that are parent of the given path
        """
        res = []
        for p in [path] + list(path.parents):
            try:
                # mini-projects
                if p.parent.name in ["draft", "wip", "unsorted", "paused"]:
                    logger.debug(f"Found mini-project: {p}")
                    res.append(p)

                # main destinations
                # todo: use destinations registry instead!
                if p.parent.name in ["experiments", "archive", "projects"]:
                    logger.debug(f"Found main project: {p}")
                    res.append(p)

                # todo: think if any other heuristics are needed here
            except:
                pass
        return list(sorted(str(p) for p in res))
