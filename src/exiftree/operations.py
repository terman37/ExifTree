from ntpath import isfile
from re import Match


import filecmp
from logging import Logger
import logging
import os
import shutil
import re

logger: Logger = logging.getLogger(name=__name__)


def operate_file(src, dest, action, dry_run) -> None:
    if dest:
        if dry_run:
            logger.info("[DRY RUN] Would %s file: %s -> %s", action, src, dest)
        else:
            logger.info("%s file: %s -> %s", action, src, dest)
            try:
                os.makedirs(name=os.path.dirname(dest), exist_ok=True)
                if action == "copy":
                    shutil.copy2(src, dst=dest)
                elif action == "move":
                    shutil.move(src, dst=dest)
            except OSError as e:
                logger.error("Failed to %s %s to %s: %s", action, src, dest, e)


def deduplicate(src: str, dest: str, duplicates_path: str, action: str, drop_duplicates: bool) -> str | None:
    file: str = os.path.basename(src)
    destination: str = os.path.join(dest, file)

    filename, extension = os.path.splitext(file)
    match: Match[str] | None = re.search(r"_(\d{1,3})$", filename)

    if match:
        base_name = filename[: match.start()]
        version = int(match.group(1))
    else:
        base_name = filename
        version = None

    # find the correct destination path
    while True:
        # Construct the candidate path based on the current version
        if version is None:
            candidate_name = f"{base_name}{extension}"
        else:
            candidate_name = f"{base_name}_{version}{extension}"

        current_dest = os.path.join(dest, candidate_name)

        # File doesn't exist
        if not os.path.isfile(current_dest):
            if current_dest != destination:
                logger.info("New destination determined: %s", current_dest)
            return current_dest

        # File Exists, Check if it's the same
        if filecmp.cmp(src, current_dest, shallow=False):
            if action == "copy":
                logger.info("Exact same file already exists at (%s). Skipping.", current_dest)
                return None

            # For move, put it in duplicate folder
            if drop_duplicates:
                os.remove(src)
                return None
            else:
                duplicate_dest = os.path.join(duplicates_path, os.path.basename(current_dest))
                logger.info("Exact same file found at (%s). Routing to duplicates: %s", current_dest, duplicate_dest)
                return duplicate_dest

        # File exists but content is different, increment suffix
        if version is None:
            version = 1
        else:
            version += 1
