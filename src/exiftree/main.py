import logging
from exiftree.config import Config
from exiftree.path_resolver import resolve_target_paths
from exiftree.scanner import scan_directory
from exiftree.operations import (
    copy_files,
    move_files,
    preview_copy_files,
    preview_move_files,
)

logger = logging.getLogger(__name__)


def main() -> None:
    # Read config
    conf: Config = Config()  # type: ignore[call-arg]  # pyright: ignore[reportCallIssue]

    # Initialize logging
    logging.basicConfig(
        level=conf.global_settings.log_level.upper(),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logger.info("Starting exiftree processing")

    # Find input files
    input_files: list[str] = []
    for folder in conf.input_folders:
        logger.info("Scanning folder: %s (max_depth: %d)", folder.path, folder.max_depth)
        found = scan_directory(folder=folder.path, extensions=conf.file_filters.extensions, max_depth=folder.max_depth)
        logger.info("Found %d matching files in %s", len(found), folder.path)
        input_files += found

    logger.info("Total files to process: %d", len(input_files))

    # Define output path target for each file
    targets: dict[str, str] = resolve_target_paths(
        files_path=input_files,
        base_path=conf.output_folder.base_path,
        template=conf.output_folder.template,
        min_width=conf.file_filters.min_width,
        min_height=conf.file_filters.min_height,
    )

    # Perform file operations
    if conf.global_settings.dry_run:
        if conf.action == "move":
            preview_move_files(targets=targets)
        else:
            preview_copy_files(targets=targets)
    else:
        if conf.action == "move":
            move_files(targets=targets)
        else:
            copy_files(targets=targets)

    logger.info("Processing complete")


if __name__ == "__main__":
    main()
