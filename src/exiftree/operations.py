import logging
import os
import shutil

logger = logging.getLogger(__name__)


def copy_files(targets: dict[str, str]) -> None:
    for src, dest in targets.items():
        logger.info("Copying file: %s -> %s", src, dest)
        try:
            os.makedirs(name=os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src, dst=dest)
        except OSError as e:
            logger.error("Failed to copy %s to %s: %s", src, dest, e)


def move_files(targets: dict[str, str]) -> None:
    for src, dest in targets.items():
        logger.info("Moving file: %s -> %s", src, dest)
        try:
            os.makedirs(name=os.path.dirname(dest), exist_ok=True)
            shutil.move(src, dst=dest)
        except OSError as e:
            logger.error("Failed to move %s to %s: %s", src, dest, e)


def preview_copy_files(targets: dict[str, str]) -> None:
    for src, dest in targets.items():
        logger.info("[DRY RUN] Would copy file: %s -> %s", src, dest)


def preview_move_files(targets: dict[str, str]) -> None:
    for src, dest in targets.items():
        logger.info("[DRY RUN] Would move file: %s -> %s", src, dest)
