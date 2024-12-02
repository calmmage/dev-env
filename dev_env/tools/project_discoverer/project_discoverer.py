from pathlib import Path
from typing import Optional

from dev_env.tools.project_discoverer.pd_config import ProjectDiscovererConfig


class ProjectDiscoverer:
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).parent / "pd_config.yaml"
        self.config = ProjectDiscovererConfig.from_yaml(config_path)
