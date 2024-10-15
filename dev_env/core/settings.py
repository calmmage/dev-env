from pydantic_settings import BaseSettings
from pathlib import Path
from pydantic import SecretStr, Field


class MySettings(BaseSettings):

    root_dir: Path = Path("~/work").expanduser()
    symlinks_dir: Path = Path("~/code").expanduser()
    env_dir: Path = Path("~/.calmmage").expanduser()

    notifications_bot_token: SecretStr = Field("", alias="NOTIFICATIONS_BOT_TOKEN")

    main_projects: list[str] = [
        # persistent
        "calmlib",
        "bot-lib",
        "calmapp",
        "examples",
        "calmmage-private",
        # not sure yet, but probably persistent
        "calmmage-service-registry",
        # 'calmmage-personal-website', is this the right name?
        "codechat",
        "outstanding-items-bot",
    ]

    # ["calmmage", "Augmented-development", "engineering-friends", "lavrpetrov"]
    accounts_to_clone_from: list[str] = [
        "calmmage",
        "engineering-friends",
    ]

    # structural_dirs: list[str] = [
    #     'seasonal',
    #     'experiments',
    #     'projects',
    #     'archive',
    #     'contexts',
    # ]

    github_api_token: SecretStr = Field(..., alias="GITHUB_API_TOKEN")

    seasonal_dir_template_repo: str = "calmmage/seasonal-dir-template"
    default_github_template: str = "calmmage/python-project-template"

    class Config:
        env_prefix = "CALMMAGE_DEV_ENV_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# todo: make a singleton?
settings = MySettings()
