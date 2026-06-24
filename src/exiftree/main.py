from typing import Any


from exiftree import define_output
from exiftree.config import Config
from exiftree.find_files import find_files
from exiftree.define_output import define_output


def main():
    print("Hello from exiftree!")


if __name__ == "__main__":
    # Read config
    conf: Config = Config()  # pyright: ignore[reportCallIssue]

    # Find input files
    input_files: list[str] = []
    for folder in conf.inputFolders:
        input_files += find_files(folder=folder.path, extensions=conf.extensions, max_depth=folder.max_depth)

    # Define output path target for each file
    targets: dict[str, str] = define_output(input_files, conf.outputFolder.base_path, conf.outputFolder.template)

    # Move files

    main()
