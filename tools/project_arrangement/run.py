import argparse
from pathlib import Path
from loguru import logger
from main import ProjectArranger

def main(config_path: str = "config.yaml", dry_run: bool = True):
    logger.info(f"Running project arranger with config from {config_path}")
    
    if dry_run:
        logger.info("Running in dry-run mode")
    
    try:
        arranger = ProjectArranger(Path(config_path))
        arranger.build_projects_list()
        arranger.sort_projects()
        arranger.print_results()
        
        if not dry_run:
            logger.warning("Apply mode not yet implemented. Use --dry-run to see what would be done.")
            
    except Exception as e:
        logger.error(f"Error during project arrangement: {e}")
        raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Project arrangement tool')
    parser.add_argument('--config', default='config.yaml', help='Path to config file')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode without making changes')
    
    args = parser.parse_args()
    main(config_path=args.config, dry_run=args.dry_run)
