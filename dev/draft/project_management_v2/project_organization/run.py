import argparse
from pathlib import Path

from loguru import logger

from dev.draft.project_management_v2.project_organization.old.main import ProjectArranger


def main(config_path: str = "config.yaml", dry_run: bool = True, verbose: bool = False):
    logger.info(f"Running project arranger with config from {config_path}")

    if dry_run:
        logger.info("Running in dry-run mode")

    try:
        arranger = ProjectArranger(Path(config_path))
        projects = arranger.build_projects_list()
        groups = arranger.sort_projects(projects)
        arranger.print_results(groups, print_sizes=verbose)

        if not dry_run:
            logger.warning(
                "Apply mode not yet implemented. Use --dry-run to see what would be done."
            )

    except Exception as e:
        logger.error(f"Error during project arrangement: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Project arrangement tool")
    default_config_path = Path(__file__).parent / "config.yaml"
    parser.add_argument("--config", default=default_config_path, help="Path to config file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode without making changes",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print additional information like project sizes",
    )

    args = parser.parse_args()
    main(config_path=args.config, dry_run=args.dry_run, verbose=args.verbose)
