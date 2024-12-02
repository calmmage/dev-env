from pathlib import Path
from typing import Annotated, Optional

import pyperclip
import typer
from rich.console import Console

from dev_env.tools.project_manager.project_manager import ProjectManager

pm = ProjectManager()
app = typer.Typer()


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
    name: str,
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
    console.print(f"✨ [green]Project created at:[/] {project_dir}. Path copied to clipboard.")
    pyperclip.copy(str(project_dir.absolute()))


# endregion New Project

# ------------------------------------------------------------
# region Mini Project
# ------------------------------------------------------------


@app.command(name="new-mini-project", help="Create a new mini-project in seasonal folder structure")
def new_mini_project(
    name: str,
    description: Annotated[
        Optional[str],
        typer.Option(
            "--description",
            "-d",
            help="Project description or idea",
        ),
    ] = None,
    private: Optional[bool] = None,
):
    """Create a new mini-project in seasonal folder structure"""

    # if user didn't specify private, ask
    if private is None:
        private = typer.confirm("Create in private repository?", default=False)

    project_dir = pm.create_mini_project(name, description, private)
    console.print(f"✨ [green]Mini-project created at:[/] {project_dir}. Path copied to clipboard.")
    pyperclip.copy(str(project_dir.absolute()))


# endregion Mini Project

# ------------------------------------------------------------
# region WIP
# ------------------------------------------------------------


@app.command(name="move-to-examples", help="Move a file or directory to examples destination")
def move_to_examples(path: Path):
    """Move a file or directory to examples destination"""
    result = pm.move_to_examples(path)
    console.print(f"✨ [green]Moved to examples:[/] {result}")


# from pathlib import Path
# from typing import Optional

# from pydantic import BaseModel, Field

# import typer
# from loguru import logger
# from calmlib.utils.gpt_utils import query_gpt

# from dev_env.tools.project_manager.project_manager import ProjectManager


# DEFAULT_CONFIG = Path(__file__).parent / "config.yaml"

# class ResponseModel(BaseModel):
#     """Response from AI about whether input is a project name or idea."""

#     is_project_name: bool = Field(description="Whether the input is already a project name")
#     suggested_name: Optional[str] = Field(
#         default=None,
#         description="Suggested project name if input was an idea"
#     )

# def validate_name_with_ai(name: str) -> Tuple[bool, Optional[str]]:
#     """Validate a name with AI"""
#     response = query_gpt(
#         prompt=name,
#         system="Is the following a project name or more broadly an idea? If it's an idea, suggest a short name for the project.",
#         structured_output_schema=ResponseModel,
#     )

#     if response.is_project_name:
#         return  name, name # name, description
#     else:
#         return response.suggested_name, name

# def check_name(name, description=None):
#     """Check if name is present and valid. If not - get it from user."""
#     result = ""
#     while not result:
#         if name:
#             # check if name is good.. ?
#             # check if name is already taken
#             result = name
#         else:
#             if description:
#                 name, description = validate_name_with_ai(description)
#             else:
#                 user_response = typer.prompt("What do you want to do? (name or idea)")
#                 if user_response:
#                     name, description = validate_name_with_ai(user_response)
#             result = name
#     return result, description


# @app.command()
# def new_project(
#     name: Optional[str] = None,
#     description: Optional[str] = None,
#     private: bool = False,
#     config: Path = DEFAULT_CONFIG,
# ):
#     """Create a new project"""
#     name, description = check_name(name, description)

#     manager = ProjectManager(config)
#     manager.create_project(name, description, private)


# @app.command()
# def new_mini_project(
#     name: Optional[str] = None,
#     description: Optional[str] = typer.Option(None, "--description", "-d", help="Project description"),
#     private: bool = typer.Option(True, "--public/--private", help="Create in public or private repository"),
#     config: Path = typer.Option(DEFAULT_CONFIG, "--config", "-c", help="Path to config file"),
# ):
#     """
#     Create a new mini-project in the seasonal folder structure.
#     If no name is provided, you will be prompted for one.
#     """
#     name, description = check_name(name, description)


#     try:
#         manager = ProjectManager(config)
#         project_dir = manager.create_mini_project(name, description, private)
#         console.print(f"✨ [green]Mini-project created at:[/] {project_dir}")
#     except Exception as e:
#         console.print(f"[red]Error:[/] {str(e)}")
#         raise typer.Exit(1)


# @app.command()
# def new_todo(
#     name: Optional[str] = None,
#     project: Optional[str] = None,
#     config: Path = DEFAULT_CONFIG,
# ):
#     """Create a new todo file"""
#     # todo: use project discoverer to find the project by name
#     # by default - use current directory project
#     manager = ProjectManager(config)
#     manager.create_todo(name, project)


# @app.command()
# def new_feature(
#     name: str,
#     description: Optional[str] = None,
#     project: Optional[str] = None,
#     config: Path = DEFAULT_CONFIG,
# ):
#     """Create a new feature draft"""
#     # todo: use project discoverer to find the project by name
#     # by default - use current directory project
#     manager = ProjectManager(config)
#     manager.create_feature(name, description, project)

# endregion WIP

if __name__ == "__main__":
    app()
