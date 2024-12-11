import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

import git
from loguru import logger

from calmlib.utils.main import is_subsequence
from dev_env.core.pm_utils.destinations import Destination, DestinationsRegistry
from dev_env.core.pm_utils.project_utils import ProjectDiscovery
from dev_env.tools.project_manager.pm_config import ProjectManagerConfig


class ProjectManager:
    def __init__(
        self, config_path: Optional[Path] = None, destinations_config_path: Optional[Path] = None
    ):
        """Initialize Project Manager with configuration"""
        if config_path is None:
            config_path = Path(__file__).parent / "pm_config.yaml"

        self.config = ProjectManagerConfig.from_yaml(config_path)
        self.discovery = ProjectDiscovery()
        self.destinations = DestinationsRegistry(destinations_config_path)
        self._github_token = None
        self._github_client = None
        self._templates = None

    # ------------------------------------------------------------
    # region GitHub
    # ------------------------------------------------------------

    @property
    def github_token(self) -> str:
        """Get GitHub token from environment variables"""
        if self._github_token is None:
            # Try to load from ~/.env first, then system env vars
            env_path = Path.home() / ".env"
            if env_path.exists():
                from dotenv import load_dotenv

                load_dotenv(env_path)

            token = os.getenv("GITHUB_API_TOKEN")
            if token is None:
                raise ValueError(
                    "Missing GitHub API token. "
                    "Please add it to ~/.env or system environment variables. "
                )
            self._github_token = token
        return self._github_token

    @property
    def github_client(self):
        """Get GitHub client instance"""
        if self._github_client is None:
            from github import Github

            self._github_client = Github(self.github_token)
        return self._github_client

    # todo: cache locally on disk?
    def get_templates(self, reset_cache=False):
        """Get all available GitHub templates"""
        if self._templates is None or reset_cache:
            repos = self.github_client.get_user().get_repos()
            self._templates = {repo.name: repo for repo in repos if repo.is_template}
        return self._templates

    @staticmethod
    def _fuzzy_match_template_name(
        incomplete: str, candidates: list[Tuple[str, str]]
    ) -> list[Tuple[str, str]]:
        """Fuzzy match the template name from candidates."""
        matches = []
        # step 1 - match by exact prefix
        for template, help_text in candidates:
            if template.startswith(incomplete):
                matches.append((template, help_text))
        if len(matches) == 1:
            return matches

        # step 2 - match by any subsequence
        for template, help_text in candidates:
            if is_subsequence(incomplete, template):
                matches.append((template, help_text))

        if len(matches) == 1:
            return matches
        # hack: always add the incomplete string to avoid typer error (broken completion)
        # todo: report the issue to typer
        matches.append((incomplete, ""))
        return matches

    def complete_template_name(self, incomplete: str) -> list[Tuple[str, str]]:
        """Complete template name with fuzzy matching."""
        templates_dict = self.get_templates()  # This returns a dict: {template_name: repo_object}
        # Transform the dict into a list of tuples (template_name, help_text)
        candidates = [(name, repo.description or "") for name, repo in templates_dict.items()]
        matches = self._fuzzy_match_template_name(incomplete, candidates)
        return matches

    def _create_repo_from_template(
        self, name: str, template_name: str, dry_run: bool = False
    ) -> str:
        """Create a new GitHub repository from template"""
        logger.debug(f"Creating repository {name} from template: {template_name}")

        github_client = self.github_client
        username = github_client.get_user().login

        # Validate template
        templates = self.get_templates()
        if template_name not in templates:
            raise ValueError(
                f"Invalid template: {template_name}. Available: {list(templates.keys())}"
            )

        # Check if repo exists
        if name in [repo.name for repo in github_client.get_user().get_repos()]:
            raise ValueError(f"Repository already exists: https://github.com/{username}/{name}")

        # Create repo from template
        params = {
            "verb": "POST",
            "url": f"/repos/{username}/{template_name}/generate",
            "input": {"owner": username, "name": name},
        }
        if not dry_run:
            github_client._Github__requester.requestJsonAndCheck(**params)

            url = f"https://github.com/{username}/{name}"
            logger.debug(f"Repository created: {url}")
            return url
        else:
            logger.info(f"Dry run: would have created repository {params}")

    def _clone_github_repository(
        self, name: str, project_dir: Path, retries: int = 3, retry_delay: int = 5
    ):
        """Clone GitHub repository to local directory"""
        project_dir = Path(project_dir)
        username = self.github_client.get_user().login
        url = f"https://{self.github_token}@github.com/{username}/{name}.git"

        if project_dir.exists() and list(project_dir.iterdir()):
            raise ValueError(f"Project directory not empty: {project_dir}")

        for i in range(retries):
            try:
                repo = git.Repo.clone_from(url, str(project_dir))
                repo.git.pull()

                # Verify clone success
                if not (project_dir / ".git").exists():
                    raise ValueError("Git directory not found")

                logger.debug(f"Repository cloned successfully to {project_dir}")
                return project_dir

            except Exception as e:
                logger.warning(f"Clone attempt {i+1} failed: {e}")
                if i < retries - 1:
                    import time

                    time.sleep(retry_delay)
                    continue
                raise

    def _check_github_conflicts(self, name: str) -> bool:
        """Check if name conflicts with existing GitHub repos"""
        try:
            # Try to get repo - if it exists, there's a conflict
            self.github_client.get_user().get_repo(name)
            return True
        except Exception:
            # If repo not found, no conflict
            return False

    # endregion GitHub

    # ------------------------------------------------------------
    # region New Project
    # ------------------------------------------------------------

    def _get_experiments_destination(self) -> Path:
        """Get experiments destination from config"""
        dest_key = self.config.experiments_destination
        return self.destinations.get(dest_key).path

    def create_project(
        self,
        name: str,
        # todo: put description into dev/idea.md or something.
        description: Optional[str] = None,
        # private: bool = False, # - later - if we want to create private repos
        template: Optional[str] = None,
        dry_run: bool = False,
    ):
        """Create a new project in experiments using GitHub template."""
        # 1. determine template
        if template is None:
            template = "python-project-template"
        else:
            matches = self.complete_template_name(template)
            if len(matches) == 1:
                template = matches[0][0]
            else:
                raise ValueError(f"Ambiguous template name: {template}. Matches: {matches}")

        if self.config.always_use_hyphens and ("_" in name):
            name = name.replace("_", "-")
            logger.info(f"Auto converted underscores to hyphens in project name: {name}")

        # Check GitHub conflicts
        if self._check_github_conflicts(name):
            raise ValueError(f"Project name '{name}' conflicts with existing GitHub repository")

        # 2. Project Creation
        try:
            # Create repo from template
            self._create_repo_from_template(name, template, dry_run)

            # Get destination from config
            destination = self._get_experiments_destination()
            project_dir = destination / name
            # todo: check if exists? and not empty?
            if project_dir.exists():
                if list(project_dir.iterdir()):
                    raise ValueError(
                        f"Project directory already exists and is not empty: {project_dir}"
                    )
                else:
                    # remove empty dir
                    project_dir.rmdir()
                    logger.warning(
                        f"Removed pre-existing empty project directory from experiments:"
                        f" {project_dir}"
                    )

            if not dry_run:
                self._clone_github_repository(name, project_dir)
            else:
                logger.info(f"Dry run: would have cloned to {project_dir}")

        except Exception as e:
            logger.error(f"Failed to create GitHub project: {e}")
            raise

        logger.info(f"Project '{name}' created successfully at {project_dir}")
        return project_dir

    # endregion New Project

    # ------------------------------------------------------------
    # region Mini Project
    # ------------------------------------------------------------

    # def _get_seasonal_folder(self) -> Path:
    #     """Get or create appropriate seasonal folder based on count and time thresholds"""
    #     now = datetime.now()
    #     month_name = now.strftime("%b").lower()
    #     year = now.year

    #     # Get base seasonal directory
    #     dest_key = (
    #         self.config.mini_projects_destination
    #         if self.config.mini_projects_destination
    #         else "calmmage-private"
    #     )
    #     destination = self.destinations.get(dest_key)
    #     seasonal_base = destination.path / "seasonal"

    #     # Find current season folder
    #     latest_link = seasonal_base / "latest"
    #     if latest_link.exists() and latest_link.is_symlink():
    #         current_folder = Path(os.readlink(latest_link))

    #         # Count projects in current folder
    #         project_count = sum(1 for p in current_folder.iterdir()
    #                           if p.is_dir() and not p.is_symlink())

    #         # Check if we need to roll over
    #         need_new_folder = (
    #             project_count >= self.config.seasonal_folder_threshold or
    #             month_name not in current_folder.name  # Month changed
    #         )

    #         if not need_new_folder:
    #             return current_folder

    #     # Create new seasonal folder
    #     existing_seasons = [p for p in seasonal_base.glob("season_*") if p.is_dir()]
    #     season_num = len(existing_seasons) + 1

    #     new_folder = seasonal_base / f"season_{season_num}_{month_name}_{year}"
    #     new_folder.mkdir(parents=True, exist_ok=True)

    #     # Update latest symlink
    #     if latest_link.exists():
    #         latest_link.unlink()
    #     latest_link.symlink_to(new_folder)

    #     return new_folder

    # def _process_mini_project_name(self, name: Optional[str]) -> str:
    #     """Process and validate mini project name"""
    #     if name is None:
    #         name = input("What mini-project do you want to create?\n").strip()

    #     # Validate with AI
    #     is_valid, suggestion = self._validate_name_with_ai(name)
    #     if not is_valid and suggestion:
    #         logger.info(f"Using AI suggested name: {suggestion}")
    #         name = suggestion

    #     return name

    # def create_mini_project(
    #     self,
    #     name: Optional[str] = None,
    #     idea: Optional[str] = None,
    #     private: bool = True
    # ) -> Path:
    #     """Create a new mini-project in seasonal folder structure"""

    #     seasonal_folder = self._get_seasonal_folder()
    #     project_dir = seasonal_folder / name

    #     # Create project directory
    #     project_dir.mkdir(exist_ok=False)  # Fail if exists

    #     # 3. Handle project idea
    #     if idea is None and not private:  # Only prompt for public projects
    #         idea = input("What's the project idea?\n").strip()

    #     if idea:
    #         idea_file = project_dir / "idea.md"
    #         idea_file.write_text(f"# Project Idea\n\n{idea}\n")

    #     # 4. Copy path to clipboard
    #     abs_path = str(project_dir.absolute())
    #     pyperclip.copy(abs_path)
    #     logger.info(f"Created mini-project at: {abs_path} (copied to clipboard)")

    def _get_mini_projects_destination(self, private: bool = False) -> Destination:
        """Get mini-projects destination from config"""
        dest_key = (
            self.config.private_mini_projects_destination
            if private
            else self.config.public_mini_projects_destination
        )
        return self.destinations.get(dest_key)

    def _get_latest_seasonal_folder(self, destination: Destination) -> Path:
        """Get latest seasonal folder"""
        seasonal_base = destination.path / "seasonal"

        # option 1: check all seasonal folders
        existing_seasons = [p for p in seasonal_base.glob("season_*") if p.is_dir()]
        latest_season = None
        latest_season_num = -1
        for season in existing_seasons:
            season_num = int(season.name.split("_")[1])
            if season_num > latest_season_num:
                latest_season_num = season_num
                latest_season = season

        # option 2: check latest symlink
        latest_link = seasonal_base / "latest"
        if latest_link.exists() and latest_link.is_symlink():
            res = Path(os.readlink(latest_link))
            if res != latest_season:
                logger.warning(f"Latest symlink exists but points to {res}, not {latest_season}")

        if latest_season:
            return latest_season
        else:
            return None

    def _create_new_seasonal_folder(
        self, destination: Destination, season_num: Optional[int] = None
    ):
        """Create a new seasonal folder"""
        if season_num is None:
            season_num = 1

        date = datetime.now()
        period = self._get_period_from_date_range(date, date)
        new_folder = destination.path / "seasonal" / f"season_{season_num}_{period}_{date.year}"
        new_folder.mkdir(parents=True, exist_ok=True)

        # update latest symlink
        latest_link = destination.path / "seasonal" / "latest"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(new_folder)

        # create folder structure
        children = ["draft", "wip", "unsorted", "paused"]
        for child in children:
            (new_folder / child).mkdir(exist_ok=True)

        return new_folder

    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

    def _get_period_from_date_range(self, start: datetime, end: datetime) -> str:
        """Get season name from date range

        within a month -> this month (1-20 jan - 'jan')
        covering two months -> both
        covering a quarter -> quarter name
        """
        if start.month == end.month:
            return self.months[start.month - 1]
        elif (start.month + 1) % 12 == end.month:
            # if just 2 months
            return f"{self.months[start.month-1]}-{self.months[end.month-1]}"

        # warn if time span is too long
        if (end - start).days > 90:
            logger.warning(f"Season spans multiple quarters: {start} - {end}")
        # winter, spring, summer or fall - based on the end month
        if end.month in [12, 1, 2]:
            return "winter"
        elif end.month in [3, 4, 5]:
            return "spring"
        elif end.month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"

    def _time_to_roll_season(self, season: Path) -> bool:
        """Check if it's time to roll over to a new season"""
        # if already enough projects within season
        if len(list(season.glob("*/*"))) >= self.config.seasonal_folder_threshold:
            return True

        # or season date range grows too large / awkward
        # i need some kind of metadata for that.. ?
        metadata = self._get_season_metadata(season)
        start = datetime.fromisoformat(metadata["start"])
        end = datetime.now()
        if (end - start).days > 90:
            return True
        if (end - start).days > 60:
            # check if we're spanning multiple different quarters
            if start.month in [12, 1, 2] and end.month in [3, 4, 5]:
                return True
            elif start.month in [3, 4, 5] and end.month in [6, 7, 8]:
                return True
            elif start.month in [6, 7, 8] and end.month in [9, 10, 11]:
                return True
            elif start.month in [9, 10, 11] and end.month in [12, 1, 2]:
                return True
        return False

    def _get_season_metadata_file(self, season: Path) -> Path:
        return season / "metadata.json"

    def _parse_name_into_date_range(self, name: str) -> Tuple[datetime, datetime]:
        """Parse season name into start and end date"""
        if name.startswith("season_"):
            name = name.split("_", 2)[2]
        # check winter/spring/summer/fall
        parts = name.split("_")
        if len(parts) == 2:
            # year_winter
            year = int(parts[1])
            season = parts[0]
            if season == "winter":
                start = datetime(year, 12, 1)
                end = datetime(year + 1, 2, 28)
            elif season == "spring":
                start = datetime(year, 3, 1)
                end = datetime(year, 5, 31)
            elif season == "summer":
                start = datetime(year, 6, 1)
                end = datetime(year, 8, 31)
            elif season == "fall":
                start = datetime(year, 9, 1)
                end = datetime(year, 11, 30)
            else:
                # month
                # or month range
                if season in self.months:

                    m = self.months.index(season) + 1
                    me = (m + 1) % 12
                    ye = year + (m + 1) // 12
                    start = datetime(ye, m, 1)
                    end = datetime(ye, me, 1) - timedelta(days=1)
                else:
                    if "-" in season:
                        start_month, end_month = season.split("-")
                        start = datetime(year, self.months.index(start_month) + 1, 1)
                        end = datetime(year, self.months.index(end_month) + 2, 1) - timedelta(
                            days=1
                        )
                    else:
                        raise ValueError(f"Invalid season name: {name}")

        else:
            raise ValueError(f"Invalid season name: {name}")

        return start, end

    def _init_season_metadata(self, season: Path):
        """Initialize season metadata"""
        metadata_file = self._get_season_metadata_file(season)
        start, end = self._parse_name_into_date_range(season.name)
        metadata = {
            "start": start.isoformat(),
            "end": end.isoformat(),
        }
        metadata_file.write_text(json.dumps(metadata))
        return metadata

    def _get_season_metadata(self, season: Path) -> dict:
        """Get season metadata"""
        metadata_file = self._get_season_metadata_file(season)
        if metadata_file.exists():
            return json.loads(metadata_file.read_text())
        else:
            return self._init_season_metadata(season)

    def _update_season_dates(
        self, season: Path, start: Optional[datetime] = None, end: Optional[datetime] = None
    ) -> Path:
        """Update season name to the latest date range"""
        metadata = self._get_season_metadata(season)
        _, num, period, year = season.name.split("_")
        if start is None:
            start = datetime.fromisoformat(metadata["start"])
        if end is None:
            end = datetime.fromisoformat(metadata["end"])
        period = self._get_period_from_date_range(start, end)

        # update metadata
        metadata = {"start": start.isoformat(), "end": end.isoformat()}
        metadata_file = self._get_season_metadata_file(season)
        metadata_file.write_text(json.dumps(metadata))

        return season.with_name(f"season_{num}_{period}_{year}")

    def get_seasonal_folder(self, private: bool = False) -> Path:
        """Get or create appropriate seasonal folder based on count and time thresholds"""
        destination = self._get_mini_projects_destination(private=private)
        # - check if time to roll
        latest_season = self._get_latest_seasonal_folder(destination)
        if latest_season is None:
            # create new
            latest_season = self._create_new_seasonal_folder(destination)
        elif self._time_to_roll_season(latest_season):
            # roll over
            latest_season = self._create_new_seasonal_folder(
                destination, latest_season.name.split("_")[1]
            )

        # - sanity check name
        latest_season = self._update_season_dates(latest_season, end=datetime.now())

        return latest_season

    #     return project_dir
    def create_mini_project(
        self, name: str, idea: Optional[str] = None, private: bool = False, dry_run: bool = False
    ) -> Path:
        """Create a new mini-project in seasonal folder structure"""
        # - locate seasonal dir
        seasonal_folder = self.get_seasonal_folder(private=private)

        if self.config.always_use_hyphens:
            if "_" in name:
                name = name.replace("_", "-")
                logger.info(f"Auto converted underscores to hyphens in project name: {name}")

        # - create dir
        project_dir = seasonal_folder / "draft" / name
        if project_dir.exists():
            if list(project_dir.iterdir()):
                raise ValueError(
                    f"Project directory already exists and is not empty: {project_dir}"
                )
            else:
                logger.warning(f"Directory already exists but is empty: {project_dir}")

        if not dry_run:
            project_dir.mkdir(exist_ok=True)

            # - put idea there
            idea_file_path = project_dir / "idea.md"
            idea_file_path.write_text(f"# {name}\n\n{idea}\n")
        else:
            logger.info(f"Dry run: Would create directory at {project_dir}")
            if idea:
                logger.info(f"Dry run: Would create idea.md with content:\n# {name}\n\n{idea}\n")

        # - print & copy path / open it.
        return project_dir

    # endregion Mini Project

    # ------------------------------------------------------------
    # region WIP
    # ------------------------------------------------------------

    def _validate_name_with_ai(self, name: str) -> tuple[bool, Optional[str]]:
        """Validate name with AI and optionally get suggestion"""
        # TODO: Implement actual AI validation using query_gpt
        # prompt = f"""Is '{name}' a good project name? Consider:
        # - Clarity and descriptiveness
        # - Length (should be concise)
        # - Standard naming conventions
        #
        # Return format:
        # VALID: true/false
        # SUGGESTION: better-name (only if VALID is false)
        # """
        # Placeholder implementation
        return True, None

    # def create_todo(
    #     self,
    #     name: Optional[str] = None,
    #     project: Optional[str] = None
    # ):
    #     """Create a new todo file"""
    #     if project is None:
    #         project = self.discovery.get_current_project()

    #     if name is None:
    #         name = datetime.now().strftime(self.config.todo_filename_template)

    #     todo_path = Path(project) / self.config.todo_subfolder / name
    #     logger.info(f"Creating todo at {todo_path}")
    #     raise NotImplementedError()

    # def create_feature(
    #     self,
    #     name: str,
    #     description: Optional[str] = None,
    #     project: Optional[str] = None
    # ):
    #     """Create a new feature draft"""
    #     if project is None:
    #         project = self.discovery.get_current_project()

    #     feature_path = Path(project) / self.config.features_subfolder / name
    #     logger.info(f"Creating feature at {feature_path}")
    # raise NotImplementedError()

    # endregion WIP

    def _get_examples_destination(self) -> Path:
        """Get examples destination from config"""
        dest_key = "examples"
        return self.destinations.get(dest_key).path

    def move_to_examples(self, path: Path):
        """Move a file or directory to examples destination"""
        examples_dest = self._get_examples_destination()
        unsorted = examples_dest / "unsorted"
        unsorted.mkdir(exist_ok=True)
        # check if exists
        target = unsorted / path.name
        if target.exists():
            logger.warning(f"Target already exists: {target}. Skipping.")
            if path.is_dir():
                target = target.with_suffix(f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            else:
                target = target.with_suffix(
                    f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{path.suffix}"
                )

        path.rename(target)
        logger.debug(f"Moved {path} to examples/unsorted at {target}")
        return target

    def open_in_editor(self, path: Path):
        """Open a file in the default editor"""
        cmd = self.config.default_editor
        cmd += f" {path}"
        logger.debug(f"Opening {path} in {cmd}")
        os.system(cmd)

    def rollup_todos(self, project_dir: Optional[Path] = None) -> Optional[Path]:
        """Roll up old todo_{date}.md files into a single todo.md file.
        Excludes today's todo file from the rollup.

        Args:
            project_dir: Project directory to check. If None, uses current project.

        Returns:
            Path to the rolled-up todo.md file if any todos were found, None otherwise.
        """
        if project_dir is None:
            project_dir = self.discovery.get_current_project()

        # Get todo directory
        todo_dir = project_dir / self.config.todo_subfolder
        if not todo_dir.exists():
            logger.debug(f"No todo directory found at {todo_dir}")
            return None

        # Get today's todo filename to exclude it
        today_filename = datetime.now().strftime(self.config.todo_filename_template)

        # Find all todo files except today's
        todo_files = [f for f in todo_dir.glob("todo_*.md") if f.name != today_filename]

        if not todo_files:
            logger.debug("No old todo files found to roll up")
            return None

        # Sort files by date (newest first)
        todo_files.sort(reverse=True)

        # Create rolled up content
        rolled_content = []
        for todo_file in todo_files:
            # Extract date from filename (assuming format todo_17_Nov.md)
            date_str = todo_file.stem.replace("todo_", "")
            try:
                date = datetime.strptime(date_str, "%d_%b")
                header = f"# Todos from {date.strftime('%d %b')}\n\n"
            except ValueError:
                # If filename doesn't match expected format, use filename as header
                header = f"# {todo_file.stem}\n\n"

            content = todo_file.read_text().strip()
            rolled_content.append(f"{header}{content}\n\n")
        # Write rolled up content
        rolled_up_path = todo_dir / "todo.md"
        if rolled_up_path.exists():
            existing_content = rolled_up_path.read_text()
            rolled_content.append(existing_content)
        rolled_up_path.write_text("".join(rolled_content))
        # Delete old files
        for todo_file in todo_files:
            todo_file.unlink()
        logger.info(f"Rolled up {len(todo_files)} todo files into {rolled_up_path}")

        return rolled_up_path
