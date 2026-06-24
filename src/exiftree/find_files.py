import os
from re import Pattern
import re


def find_files(folder, extensions, max_depth=1) -> list[str]:

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
            continue

    return matched_files
