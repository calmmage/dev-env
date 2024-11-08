"""
a script that deploys some basic version of the dev environment

- ~/work
-> all repos, including main ones
- ~/code
~ seasonal dir

"""

from dev_env import repo_root
from pathlib import Path

from dev_env.core.ffs import setup_seasonal_folder, create_dirs, setup_symlinks_dir, clone_projects
from dev_env.setup.setup_shell_profiles_and_env import add_line_to_shell_profile_safe
from dev.draft.mvp import project_manager


def setup_hacky_aliases_and_env_vars():
    # these both probably can be added to the resource file .zshrc in the repo
    # todo: need a script that runs and checks in the start of bashrc if $CALMMAGE_DEV_ENV_PATH is set and warn if not
    # todo: put files in a proper place and clean up and update these paths
    typer_path = "$CALMMAGE_DEV_ENV_PATH/.venv/bin/typer"
    relative_path_to_project_manager = Path(project_manager.__file__).relative_to(repo_root)
    new_project_tool_path = f"$CALMMAGE_DEV_ENV_PATH/{relative_path_to_project_manager}"
    lines_to_add = [f"alias typer='{typer_path}'", f"alias new_project='typer {new_project_tool_path}'"]
    for line in lines_to_add:
        add_line_to_shell_profile_safe(line)


def main():
    create_dirs()
    setup_hacky_aliases_and_env_vars()
    clone_projects()

    setup_seasonal_folder()

    setup_symlinks_dir()


if __name__ == "__main__":
    main()
