import subprocess
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from calmlib.utils.gpt_utils import query_gpt
from loguru import logger
from pydantic import BaseModel, Field
from rich.console import Console

console = Console()


class ProjectName(BaseModel):
    is_good_name: bool = Field(
        description="Whether the provided description is already a good name for the project"
    )
    name: str = Field(description="The name of the project")
    num_words: int = Field(description="The number of words in the name")


class EditorChoice(str, Enum):
    COPY = "copy"
    CURSOR = "cursor"
    PYCHARM = "pycharm"
    VSCODE = "vscode"


def generate_project_name(name: Optional[str] = None) -> str:
    """Generate a project name from a description."""
    if name is None:
        name = typer.prompt("What do you want to do")

    system_message = """
You're project name generator assistant.
You're given a description of a project from user.
If the description is actually already fits as a name, just return it.
Otherwise, generate a new name for the project.

1) if possible try to keep the original name, but if it's not good, generate a new one
2) maximum 3 words in the name
3) style: lowercase, with dashes, no spaces
example: "download all telegram messages" -> "load-telegram-messages"
"""

    response = query_gpt(
        name,
        system=system_message,
        structured_output_schema=ProjectName,
    )

    if response.is_good_name:
        # Format user response to lowercase and with dashes
        name = name.lower().replace(" ", "-")
        logger.info(f"The provided description is already a good name for the project: {name}")
        return name
    else:
        suggested_name = response.name
        logger.info(f"Suggested project name: {suggested_name}")
        if typer.confirm("Use this name?", default=True):
            return suggested_name
        else:
            # Recursively ask for a new name
            return generate_project_name(None)


def open_in_editor(path: Path, editor: EditorChoice):
    """Open the project in the selected editor."""
    path_str = str(path.absolute())

    if editor == EditorChoice.COPY:
        import pyperclip

        pyperclip.copy(path_str)
        console.print(f"📋 Path copied to clipboard: {path_str}")
    else:
        try:
            subprocess.run([editor.value, path_str], check=True)
            console.print(f"📂 Opened in {editor.value}: {path_str}")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to open in {editor.value}[/]")
            logger.error(f"Error opening editor: {e}")
