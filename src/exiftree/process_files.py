from logging import Logger
import logging
import os
import shutil

import exiftool
from exiftool.exceptions import ExifToolExecuteError

from exiftree.config import Config
from exiftree.media import Media
from exiftree.utils import deduplicate

logger: Logger = logging.getLogger(name=__name__)


class ExifToolMissingError(Exception):
    """Raised when the external exiftool executable is not installed on the system."""

    pass


def process_files(
    files_path: list[str],
    config: Config,
) -> None:

    # Get file metadata for all files
    try:
        with exiftool.ExifToolHelper() as et:
            raw_metadatas = et.get_metadata(files=files_path)
    except FileNotFoundError as e:
        logger.error(
            "The external dependency 'exiftool' is not installed or not found in the PATH. "
            "Please install exiftool (e.g., 'sudo apt install exiftool' or 'brew install exiftool') to run this script."
        )
        raise ExifToolMissingError("exiftool executable not found on system path") from e

    for raw_metadata in raw_metadatas:
        media: Media = Media(raw_metadata)

        logger.debug(
            "Processing file %s",
            media.file,
        )

        # Skip if image size is below expectations
        if config.file_filters.min_width > 0 or config.file_filters.min_height > 0:
            if media.width < config.file_filters.min_width or media.height < config.file_filters.min_height:
                logger.debug(
                    "  ! Skipping file: image size %dx%d is below minimum threshold %dx%d",
                    media.width,
                    media.height,
                    config.file_filters.min_width,
                    config.file_filters.min_height,
                )
                continue

        # Inject the filename-derived date into the file itself
        if config.global_settings.write_metadata_from_filename:
            tags: dict[str, str] | None = media.write_tags
            if tags:
                if config.global_settings.dry_run:
                    logger.info(
                        "  > [DRY RUN] Would write metadata %s to %s",
                        tags,
                        media.file,
                    )
                else:
                    try:
                        et.set_tags(media.file, tags)
                    except ExifToolExecuteError as e:
                        logger.error(
                            "  - Failed to write metadata %s to %s: %s",
                            tags,
                            media.file,
                            e,
                        )

        # Define destination Path
        if media.date:
            dest = media.render_path(config.output_folder.base_path_template)
            dupl_dest = media.render_path(config.output_folder.duplicates_path_template)
            dest = deduplicate(media.file, dest, dupl_dest, config.action, config.output_folder.drop_duplicates)
        else:
            logger.debug("  - No creation date found for file: Outputting to 'Unknown'")
            dest = os.path.join(
                media.render_path(config.output_folder.unknown_path_template),
                os.path.basename(media.file),
            )

        # Operate File
        if dest:
            if config.global_settings.dry_run:
                logger.info("  > [DRY RUN] Would %s file %s to %s", config.action, media.file, dest)
            else:
                logger.info("  > %s file %s to %s", config.action, media.file, dest)
                try:
                    os.makedirs(name=os.path.dirname(dest), exist_ok=True)
                    if config.action == "copy":
                        shutil.copy2(media.file, dst=dest)
                    elif config.action == "move":
                        shutil.move(media.file, dst=dest)
                except OSError as e:
                    logger.error("  - Failed to %s to %s: %s", config.action, dest, e)
