import os
import shutil


def move_files(targets: dict[str, str]):

    for src, dest in targets.items():
        os.makedirs(name=os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src, dst=dest)
