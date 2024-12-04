from pathlib import Path
from typing import Annotated, List

import pyperclip
import typer
from loguru import logger

from dev_env.tools.project_discoverer.project_discoverer import ProjectDiscoverer

app = typer.Typer()
pd = ProjectDiscoverer()


def show_result_menu(results: List[Path]):
    options = [f"{i}. {path}" for i, path in enumerate(results, 1)]
    options.append("0. Exit. Search more (not implemented yet)")
    # show user menu with typer
    user_choice = typer.prompt("\n".join(options), type=int)
    if user_choice == 0:
        # exiting
        return None

    return str(results[user_choice - 1].absolute())


# todo: I will need to change aliases if I add more commands
@app.command(name="find", help="Find a project by name")
def find_project(
    query: Annotated[
        str,
        typer.Argument(
            ...,
            help="Name of the project to find",
        ),
    ],
):
    """Find a project by name"""
    # Quick search in common locations
    results = pd.quick_search(query)

    if len(results) == 1:
        # copy to clipboard and print
        result = str(results[0].absolute())
    elif not results:
        logger.info("No projects found in common locations")
        logger.info("Try using 'fp_' or 'find' aliases to search with ripgrep")
        return
    else:
        result = show_result_menu(results)
        if result is None:
            return

    pyperclip.copy(result)
    typer.echo(f"✨ [green]Project found:[/] {result}. Path copied to clipboard.")


if __name__ == "__main__":
    app()
