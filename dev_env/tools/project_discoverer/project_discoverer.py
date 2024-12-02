from pathlib import Path
from typing import List, Optional

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
