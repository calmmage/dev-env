from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import yaml
from typing import List, Set, Dict
from collections import defaultdict
from loguru import logger

class Project(BaseModel):
    name: str
    path: Path
    
    @property
    def size(self) -> int:
        total_size = 0
        for file in self.path.rglob('*'):
            # Skip common non-source directories
            if any(part in str(file.relative_to(self.path)) for part in [
                '.git', '.venv', 'venv', '__pycache__', 'node_modules',
                'build', 'dist', '.pytest_cache'
            ]):
                continue
                
            # Only count source code files
            if file.is_file() and file.suffix in [
                '.py', '.js', '.ts', '.jsx', '.tsx',
                '.java', '.cpp', '.c', '.h', '.hpp',
                '.rs', '.go', '.rb', '.php', '.html',
                '.css', '.scss', '.sql', '.sh'
            ]:
                total_size += file.stat().st_size
                
        return total_size

class ProjectArrangerSettings(BaseSettings):
    # group 1: general
    dry_run: bool = True
    root_paths: List[Path]

    # group 2: manual sorting
    ignored_projects: Set[str] = set()
    main_projects: Set[str] = set()

    # group 3: auto sorting
    

    # group 4: extras
    ignored_dirs: Set[str] = {'.git', '.venv', 'venv', '__pycache__', 
                             'node_modules', 'build', 'dist', '.pytest_cache'}
    source_extensions: Set[str] = {'.py', '.js', '.ts', '.jsx', '.tsx',
                                  '.java', '.cpp', '.c', '.h', '.hpp',
                                  '.rs', '.go', '.rb', '.php', '.html',
                                  '.css', '.scss', '.sql', '.sh'}
    
    @classmethod
    def from_yaml(cls, yaml_path: str | Path, **kwargs):
        with open(yaml_path) as f:
            yaml_settings = yaml.safe_load(f)
        yaml_settings.update(**kwargs)
        return cls(**yaml_settings)

class ProjectArranger:
    def __init__(self, config_path: Path, **kwargs):
        self.settings = ProjectArrangerSettings.from_yaml(config_path, **kwargs)
        self.projects: List[Project] = []
        self.sorted_projects: Dict[str, List[Project]] = defaultdict(list)

    def build_projects_list(self) -> None:
        """Discover all projects in configured paths"""
        for root in self.settings.root_paths:
            root = root.expanduser()
            if not root.exists():
                logger.warning(f"Path {root} does not exist")
                continue
                
            for path in root.iterdir():
                if not path.is_dir():
                    continue
                if path.name.startswith('.'):
                    continue
                if path.name in self.settings.ignored_projects:
                    continue
                    
                self.projects.append(Project(
                    name=path.name,
                    path=path.resolve()
                ))

    def sort_projects(self) -> None:
        """Sort projects into categories"""
        for project in self.projects:
            if project.name in self.settings.ignored_projects:
                self.sorted_projects['ignore'].append(project)
            elif project.name in self.settings.main_projects:
                self.sorted_projects['projects'].append(project)
            else:
                # Self-referential sorting based on original path
                if 'experiments' in str(project.path):
                    self.sorted_projects['experiments'].append(project)
                elif 'archive' in str(project.path):
                    self.sorted_projects['archive'].append(project)
                else:
                    self.sorted_projects['unsorted'].append(project)

    def print_results(self) -> None:
        """Print sorted projects"""
        print("\nProject Groups:")
        for group, proj_list in self.sorted_projects.items():
            print(f"\n{group.title()}:")
            for proj in sorted(proj_list, key=lambda x: x.name):
                print(f"- {proj.name}")

