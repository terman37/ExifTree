from typing import Any


from exiftree import define_output
from exiftree.config import Config
from exiftree.find_files import find_files
from exiftree.define_output import define_output
from exiftree.move_files import move_files


def main():
    # Read config
    conf: Config = Config()  # pyright: ignore[reportCallIssue]

    # Find input files
    input_files: list[str] = []
    for folder in conf.inputFolders:
        input_files += find_files(folder=folder.path, extensions=conf.extensions, max_depth=folder.max_depth)

    # Define output path target for each file
    targets: dict[str, str] = define_output(input_files, conf.outputFolder.base_path, conf.outputFolder.template)

    # Move files
    move_files(targets=targets)


if __name__ == "__main__":
    main()
