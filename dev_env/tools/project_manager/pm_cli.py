from pathlib import Path
from typing import Annotated, Optional

import pyperclip
import typer
from rich.console import Console

from dev_env.tools.project_discoverer.project_discoverer import ProjectDiscoverer
from dev_env.tools.project_manager.project_manager import ProjectManager

pm = ProjectManager()
app = typer.Typer()
pd = ProjectDiscoverer()

console = Console()

# ------------------------------------------------------------
# region New Project
# ------------------------------------------------------------


def parse_template_name(template_name: str, candidates=None):
    """
    Parse the template name and return the correct one.
    """
    matches = list(pm.complete_template_name(template_name, candidates))
    if len(matches) == 1:
        name, _help = matches[0]
        return name
    else:
        raise typer.BadParameter(
            f"Invalid template name: {template_name}. {matches=}",
            param_hint=f"template",
        )


@app.command(
    name="new-project", help="Create a new project in github and clone to experiments destination"
)
def new_project(
    name: Annotated[
        str,
        typer.Argument(
            ...,
            help="Name of the project",
        ),
    ],
    template: Annotated[
        Optional[str],
        typer.Option(
            "--template",
            "-t",
            help="Template name for the GitHub project.",
            autocompletion=pm.complete_template_name,
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Print what would be done without actually doing it",
        ),
    ] = False,
):
    """Create a new project in github and clone to experiments destination"""
    if template:
        template = parse_template_name(template)
    project_dir = pm.create_project(name, template=template, dry_run=dry_run)
    if not dry_run:
        console.print(f"✨ [green]Project created at:[/] {project_dir}. Path copied to clipboard.")
        pyperclip.copy(str(project_dir.absolute()))
    else:
        console.print(f"✨ [yellow]Dry run:[/] Would create project at {project_dir}")


# endregion New Project

# ------------------------------------------------------------
# region Mini Project
# ------------------------------------------------------------


@app.command(name="new-mini-project", help="Create a new mini-project in seasonal folder structure")
def new_mini_project(
    name: Annotated[
        str,
        typer.Argument(
            ...,
            help="Name of the mini-project",
        ),
    ],
    description: Annotated[
        Optional[str],
        typer.Option(
            "--description",
            "-d",
            help="Project description or idea",
        ),
    ] = None,
    private: Optional[bool] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Print what would be done without actually doing it",
        ),
    ] = False,
):
    """Create a new mini-project in seasonal folder structure"""

    # if user didn't specify private, ask
    if private is None:
        private = typer.confirm("Create in private repository?", default=False)

    project_dir = pm.create_mini_project(name, description, private, dry_run=dry_run)
    if not dry_run:
        console.print(
            f"✨ [green]Mini-project created at:[/] {project_dir}. Path copied to clipboard."
        )
        pyperclip.copy(str(project_dir.absolute()))
    else:
        console.print(f"✨ [yellow]Dry run:[/] Would create mini-project at {project_dir}")


# endregion Mini Project

# ------------------------------------------------------------
# region WIP
# ------------------------------------------------------------


@app.command(name="move-to-examples", help="Move a file or directory to examples destination")
def move_to_examples(
    path: Annotated[
        Path,
        typer.Argument(
            ...,
            help="Path to the file or directory to move to examples",
        ),
    ],
):
    """Move a file or directory to examples destination"""
    result = pm.move_to_examples(path)
    console.print(f"✨ [green]Moved to examples:[/] {result}")


def get_project_dir(path: Path, mini_projects: bool = False) -> Optional[Path]:
    """
    Get the top-level project directory for the given path.
    Returns None if no project directory is found.
    """
    project_dirs = pd.get_outer_project_dirs(path)
    if mini_projects:
        return project_dirs[-1] if project_dirs else None
    else:
        return project_dirs[0] if project_dirs else None


@app.command(name="get-project", help="Get the project directory for the current path")
def get_project(
    path: Annotated[
        Optional[Path],
        typer.Argument(
            help="Path to check (defaults to current directory)",
        ),
    ] = None,
    mini_projects: Annotated[
        bool,
        typer.Option(
            "-m",
            "--mini-projects",
            help="Get the mini-project directory instead of the main project directory",
        ),
    ] = False,
):
    """Get the project directory for the given path or current directory"""
    check_path = path or Path.cwd()
    project_dir = get_project_dir(check_path, mini_projects=mini_projects)

    if project_dir:
        console.print(f"✨ [green]Project directory found:[/] {project_dir}")
    else:
        console.print("[yellow]No project directory found[/]")


# endregion WIP

if __name__ == "__main__":
    app()
