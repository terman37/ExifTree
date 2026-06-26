from logging import Logger
import logging
import os

import exiftool
from pydantic import BaseModel, Field

from exiftree.media_date import MediaDate

logger: Logger = logging.getLogger(name=__name__)


class FileMetadata(BaseModel):
    source_file: str = Field(alias="SourceFile")
    image_size: str | None = Field(default=None, alias="Composite:ImageSize")
    quicktime_create_date: str | None = Field(default=None, alias="QuickTime:CreateDate")
    exif_datetime_original: str | None = Field(default=None, alias="EXIF:DateTimeOriginal")


class ExifToolMissingError(Exception):
    """Raised when the external exiftool executable is not installed on the system."""

    pass


def resolve_target_paths(
    files_path: list[str],
    base_path: str,
    template: str,
    min_width: int = 0,
    min_height: int = 0,
) -> dict[str, str]:

    # Get file metadata
    try:
        with exiftool.ExifToolHelper() as et:
            raw_metadata = et.get_metadata(files=files_path)
    except FileNotFoundError as e:
        logger.error(
            "The external dependency 'exiftool' is not installed or not found in the PATH. "
            "Please install exiftool (e.g., 'sudo apt install exiftool' or 'brew install exiftool') to run this script."
        )
        raise ExifToolMissingError("exiftool executable not found on system path") from e

    # Validate raw dictionaries into structured models
    metadata_list: list[FileMetadata] = [FileMetadata.model_validate(metadata) for metadata in raw_metadata]

    output: dict[str, str] = {}
    for metadata in metadata_list:
        file: str = metadata.source_file
        image_size: str | None = metadata.image_size

        # Perform image size validation if requested
        if min_width > 0 or min_height > 0:
            if image_size:
                try:
                    width_str, height_str = image_size.split(" ")
                    width: int = int(width_str)
                    height: int = int(height_str)
                    if width < min_width or height < min_height:
                        logger.info(
                            "Skipping file %s: image size %dx%d is below minimum threshold %dx%d",
                            file,
                            width,
                            height,
                            min_width,
                            min_height,
                        )
                        continue
                except (ValueError, AttributeError):
                    logger.warning(
                        "Skipping file %s: failed to parse image size string '%s'",
                        file,
                        image_size,
                    )
                    continue
            else:
                logger.info(
                    "Skipping file %s: no image size metadata found, but minimum dimensions are set",
                    file,
                )
                continue

        quicktime_date: str | None = metadata.quicktime_create_date
        exif_date: str | None = metadata.exif_datetime_original

        if quicktime_date:
            file_date = quicktime_date
        elif exif_date:
            file_date = exif_date
        else:
            file_date = None

        media_date: MediaDate = MediaDate(date_str=file_date)
        if media_date.date:
            # Format targets using template keys (year, month, day)
            output[file] = os.path.join(
                base_path,
                template.format(year=media_date.year, month=media_date.month, day=media_date.day),
            )
        else:
            logger.warning("No creation date found for file: %s. Outputting to 'Unknown'", file)
            output[file] = os.path.join(base_path, "Unknown")

        output[file] = os.path.join(output[file], os.path.basename(file))

    return output
