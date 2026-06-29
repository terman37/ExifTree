from ntpath import isfile
from re import Match, Pattern


import filecmp
from logging import Logger
import logging
import os
import re

logger: Logger = logging.getLogger(name=__name__)


def scan_directory(folder: str, extensions: list[str], max_depth: int = 1) -> list[str]:
    regex_patterns: list[str] = [rf".*\.{e}$" for e in extensions]
    pattern: Pattern[str] = re.compile("|".join(regex_patterns), re.IGNORECASE)
    matched_files: list[str] = []

    stack: list[tuple[str, int]] = [(os.path.abspath(folder), 0)]

    while stack:
        current_dir, current_depth = stack.pop()
        try:
            with os.scandir(current_dir) as entries:
                for entry in entries:
                    if entry.is_file() and pattern.search(entry.name):
                        matched_files.append(entry.path)
                    elif entry.is_dir(follow_symlinks=False) and current_depth < max_depth:
                        stack.append((entry.path, current_depth + 1))
        except PermissionError:
            logger.warning("  - Permission denied accessing directory: %s", current_dir)
            continue
        except (FileNotFoundError, NotADirectoryError):
            logger.warning("  - Directory not found or is not a directory: %s", current_dir)
            continue

    return matched_files


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
                logger.debug("  - File already exists, update to: %s", candidate_name)
            return current_dest

        # File Exists, Check if it's the same
        if filecmp.cmp(src, current_dest, shallow=False):
            if action == "copy":
                logger.debug("  ! Skipping file: Exact same file already exists at (%s). ", current_dest)
                return None

            # For move, put it in duplicate folder
            if drop_duplicates:
                os.remove(src)
                return None
            else:
                duplicate_dest = os.path.join(duplicates_path, os.path.basename(current_dest))
                logger.debug("  - Exact same file found at (%s). Routing to duplicates: %s", current_dest, duplicate_dest)
                return duplicate_dest

        # File exists but content is different, increment suffix
        if version is None:
            version = 1
        else:
            version += 1
