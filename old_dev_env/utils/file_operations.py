import shutil
from pathlib import Path
from deprecated import deprecated
from loguru import logger


# @deprecated(version="0.1.0", reason="Use calmlib.beta.utils.common.copy_tree instead.")
# def copy_tree(source: Path, destination: Path, override: bool = False):
#     if not source.is_dir():
#         raise ValueError(f"Source ({source}) is not a directory.")
#
#     if not destination.exists():
#         destination.mkdir(parents=True)
#
#     for item in source.iterdir():
#         if item.is_dir():
#             copy_tree(item, destination / item.name, override=override)
#         else:
#             if override or not (destination / item.name).exists():
#                 shutil.copy2(item, destination / item.name)


def move_and_symlink(source: Path, dest: Path):
    if dest.exists():
        raise FileExistsError(f"Destination already exists: {dest}")
    shutil.move(str(source), str(dest))
    source.symlink_to(dest)


def get_backup_path(original_path: Path, suffix: str = "_backup"):
    backup_path = original_path.parent / (original_path.name + suffix)
    counter = 1
    while backup_path.exists():
        backup_path = original_path.parent / f"{original_path.name}{suffix}({counter})"
        counter += 1
    return backup_path


def get_latest_backup_path(original_path: Path, suffix: str = "_backup"):
    backup_path = original_path.parent / (original_path.name + suffix)
    counter = 1
    while True:
        next_path = original_path.parent / f"{original_path.name}{suffix}({counter})"
        if not next_path.exists():
            return backup_path
        backup_path = next_path
        counter += 1
