from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class NewProjectConfig(BaseModel):
    """Configuration for new project creation"""

    destination: str


class NewMiniProjectConfig(BaseModel):
    """Configuration for new mini-project creation"""

    private_destination: str
    public_destination: str


class NewFeatureConfig(BaseModel):
    """Configuration for new feature creation"""

    subfolder: Path


class NewTodoConfig(BaseModel):
    """Configuration for new todo creation"""

    subfolder: Path
    filename_template: str


class ProjectManagerConfig(BaseSettings):
    """Project Manager configuration"""

    targets: dict[str, BaseModel] = {
        "new_project": NewProjectConfig,
        "new_mini_project": NewMiniProjectConfig,
        "new_feature": NewFeatureConfig,
        "new_todo": NewTodoConfig,
    }
    settings: dict[str, str]

    @classmethod
    def from_yaml(cls, path: Path) -> "ProjectManagerConfig":
        """Load config from yaml file"""
        import yaml

        with open(path) as f:
            data = yaml.safe_load(f)

        # Convert target configs to appropriate models
        data["targets"] = {
            name: cls.targets[name](**config) for name, config in data["targets"].items()
        }

        return cls(**data)
