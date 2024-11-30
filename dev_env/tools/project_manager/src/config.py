from pathlib import Path
from typing import Dict

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Destination(BaseModel):
    name: str
    path: Path
    description: str


class Template(BaseModel):
    path: Path
    description: str


class ProjectManagerSettings(BaseModel):
    default_editor: str = "code"
    todo_format: str = "%Y-%m-%d"
    draft_folder: str = "dev/draft"
    todo_folder: str = "dev/todo"


class ProjectManagerConfig(BaseSettings):
    destinations: Dict[str, Destination]
    templates: Dict[str, Template]
    settings: ProjectManagerSettings

    @classmethod
    def from_yaml(cls, yaml_path: Path):
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        return cls(**data)
