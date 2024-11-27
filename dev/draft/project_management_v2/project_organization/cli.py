from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.table import Table

from dev.draft.project_management_v2.project_organization.old.main import ProjectArranger

# from .old.main import ProjectArranger

app = typer.Typer()
console = Console()

DEFAULT_CONFIG = Path("config.yaml")
MISSING_THRESHOLD = 5  # Warn if more than this many projects are missing


@app.command()
def compare(
    config: Path = typer.Option(DEFAULT_CONFIG, "--config", "-c", help="Path to config file"),
    show_ignored: bool = typer.Option(False, "--show-ignored", "-i", help="Show ignored projects"),
    # sort_by: str = typer.Option("org", "--sort-by", "-s", help="Sort by: org, edited, created, name"),
):
    """Compare local and GitHub projects lists"""
    arranger = ProjectArranger(config)

    # Get raw project lists
    local_projects = arranger._build_projets_list_local()
    github_projects = arranger._build_projets_list_github()

    if not show_ignored:
        local_projects = [p for p in local_projects if arranger._sort_main_manual(p) != "ignore"]

    # Sort function
    # def get_sort_key(project):
    #     if sort_by == "org":
    #         return (project.github_org or "", project.name)
    #     elif sort_by == "edited":
    #         return project.date
    #     elif sort_by == "created":
    #         return project.created_date
    #     return project.name
    #
    # # Sort projects
    # local_projects.sort(key=get_sort_key)
    # github_projects.sort(key=get_sort_key)
    #
    # # Print local projects
    # console.print("\n[blue]Local projects:[/blue]")
    # table = Table(show_header=True)
    # table.add_column("Name")
    # table.add_column("GitHub Info")
    # table.add_column("Last Updated")
    #
    # for proj in local_projects:
    #     github_info = f"{proj.github_org}/{proj.github_name}" if proj.github_org else "-"
    #     table.add_row(
    #         proj.name,
    #         github_info,
    #         proj.date.strftime("%Y-%m-%d"),
    #     )
    # console.print(table)
    #
    # # Print GitHub projects
    # console.print("\n[blue]GitHub projects:[/blue]")
    # table = Table(show_header=True)
    # table.add_column("Name")
    # table.add_column("Owner")
    # table.add_column("Last Updated")
    #
    # for proj in github_projects:
    #     table.add_row(
    #         proj.name,
    #         proj.github_org or "",
    #         proj.date.strftime("%Y-%m-%d"),
    #         )
    # console.print(table)

    # Print stats
    # Get project identifiers
    local_names = {(p.github_org, p.github_name) for p in local_projects if p.github_name}
    github_names = {(p.github_org, p.github_name) for p in github_projects}

    missing_locally = github_names - local_names
    missing_on_github = {(p.github_org, p.name) for p in local_projects if not p.github_name}

    # Sort by org, then name
    missing_locally = sorted(missing_locally)
    missing_on_github = sorted(missing_on_github)

    # Print results
    if missing_locally:
        console.print(f"\n[yellow]Missing locally ({len(missing_locally)}):[/yellow]")
        for org, name in missing_locally:
            proj = next(p for p in github_projects if p.github_name == name and p.github_org == org)
            console.print(f"  {org}/{name:<30} (Last updated: {proj.date.strftime('%Y-%m-%d')})")
        if len(missing_locally) > MISSING_THRESHOLD:
            console.print(
                f"\n[red]Warning: {len(missing_locally)} projects missing locally. "
                "Consider cloning them or improving filters.[/red]"
            )

    if missing_on_github:
        console.print(f"\n[yellow]Missing on GitHub ({len(missing_on_github)}):[/yellow]")
        for org, name in missing_on_github:
            proj = next(p for p in local_projects if p.name == name)
            console.print(
                f"  {org or '-'}/{name:<30} (Last edited: {proj.date.strftime('%Y-%m-%d')})"
            )
        if len(missing_on_github) > MISSING_THRESHOLD:
            console.print(
                f"\n[red]Warning: {len(missing_on_github)} projects not on GitHub. "
                "Consider pushing them or improving filters.[/red]"
            )

    if not missing_locally and not missing_on_github:
        console.print("\n[green]All projects are in sync![/green]")


if __name__ == "__main__":
    load_dotenv()
    app()
