from logging import Logger
import logging

from exiftree.config import Config
from exiftree.process_files import process_files
from exiftree.utils import scan_directory

logger: Logger = logging.getLogger(name=__name__)


def main() -> None:
    # Read config
    conf: Config = Config()  # type: ignore[call-arg]  # pyright: ignore[reportCallIssue]

    # Initialize logging
    logging.basicConfig(
        level=conf.global_settings.log_level.upper(),
        format="%(asctime)s [%(levelname)-8s] %(name)-22s: %(message)s",
    )

    logger.info("*** Starting exiftree processing ***")

    # Find input files
    input_files: list[str] = []
    for folder in conf.input_folders:
        logger.info("Scanning folder: %s (max_depth: %d)", folder.path, folder.max_depth)
        found: list[str] = scan_directory(folder=folder.path, extensions=conf.file_filters.extensions, max_depth=folder.max_depth)
        logger.debug(" - Found %d matching files in %s", len(found), folder.path)
        input_files += found

    logger.info("*** Total files to process: %d ***", len(input_files))

    # Define output path target and process each file
    if len(input_files) > 0:
        process_files(
            files_path=input_files,
            config=conf,
        )

    logger.info("*** Processing complete ***")


if __name__ == "__main__":
    main()
