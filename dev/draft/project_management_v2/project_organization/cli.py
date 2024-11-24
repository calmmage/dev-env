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
    sort_by: str = typer.Option("edited", "--sort-by", "-s", help="Sort by: edited, created, name"),
):
    """Compare local and GitHub projects lists"""
    arranger = ProjectArranger(config)

    if arranger.github_client is None:
        logger.error(
            "GitHub client not available. Please set GITHUB_API_TOKEN environment variable"
        )
        raise typer.Exit(1)

    # Get local projects
    local_projects = arranger._build_projets_list_local()
    if not show_ignored:
        local_projects = [p for p in local_projects if arranger._sort_main_manual(p) != "ignore"]

    # Get GitHub projects
    github_projects = []
    try:
        for repo in arranger.github_client.get_user().get_repos():
            if repo.fork:  # Skip forked repos
                continue
            github_projects.append(repo.name)
    except Exception as e:
        logger.error(f"Failed to get GitHub projects: {e}")
        raise typer.Exit(1)

    # Compare lists
    local_names = {p.github_name or p.name for p in local_projects}
    github_only = set(github_projects) - local_names
    local_only = {p.name for p in local_projects if not p.github_name} - set(github_projects)

    # Sort projects
    def get_sort_key(project):
        if sort_by == "edited":
            return project.date
        elif sort_by == "created":
            return project.created_date
        return project.name

    local_projects.sort(key=get_sort_key, reverse=(sort_by in ["edited", "created"]))

    # Print results
    if github_only:
        console.print("\n[yellow]GitHub projects not found locally:[/yellow]")
        for name in sorted(github_only):
            console.print(f"  {name}")
        if len(github_only) > MISSING_THRESHOLD:
            console.print(
                f"\n[red]Warning: {len(github_only)} projects missing locally. "
                "Consider cloning them or improving filters.[/red]"
            )

    if local_only:
        console.print("\n[yellow]Local projects not on GitHub:[/yellow]")
        table = Table(show_header=True)
        table.add_column("Name")
        table.add_column("Last Edited")
        table.add_column("Size")

        for proj in local_projects:
            if proj.name in local_only:
                table.add_row(
                    proj.name,
                    proj.date.strftime("%Y-%m-%d"),
                    proj.size_formatted,
                )
        console.print(table)

        if len(local_only) > MISSING_THRESHOLD:
            console.print(
                f"\n[red]Warning: {len(local_only)} projects not on GitHub. "
                "Consider pushing them or improving filters.[/red]"
            )

    if not github_only and not local_only:
        console.print("\n[green]All projects are in sync![/green]")


if __name__ == "__main__":
    load_dotenv()
    app()
