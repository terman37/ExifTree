from typing import Literal


from datetime import datetime
from logging import Logger
import logging
from re import Match, Pattern
import re

import dateutil.parser
from pydantic import BaseModel, Field

logger: Logger = logging.getLogger(name=__name__)

# Pattern to identify traditional EXIF date representation (e.g., "YYYY:MM:DD HH:MM:SS")
EXIF_DATE_PATTERN: Pattern[str] = re.compile(r"^(\d{4}):(\d{2}):(\d{2})")


class FileMetadata(BaseModel):
    source_file: str = Field(alias="SourceFile")
    image_size: str | None = Field(default=None, alias="Composite:ImageSize")
    quicktime_create_date: str | None = Field(default=None, alias="QuickTime:CreateDate")
    exif_datetime_original: str | None = Field(default=None, alias="EXIF:DateTimeOriginal")


class Media:

    def __init__(self, raw_metadata) -> None:

        # Validate raw dictionaries into structured models
        metadata: FileMetadata = FileMetadata.model_validate(raw_metadata)

        self.date_str: str | None = self.find_date(metadata)
        self.date: datetime | None = self.string_to_datetime()
        self.file = metadata.source_file
        self.width, self.height = self.get_size(metadata.image_size)

    def find_date(self, metadata) -> str | None:
        file_date: str | None = None
        if metadata.quicktime_create_date:
            file_date = metadata.quicktime_create_date
        elif metadata.exif_datetime_original:
            file_date = metadata.exif_datetime_original
        return file_date

    def get_size(self, image_size) -> tuple[int, int]:
        try:
            width_str, height_str = image_size.split(sep=" ")  # looks like "1920 1080"
        except (ValueError, AttributeError):
            logger.warning(
                "  - Failed to parse image size string '%s'",
                image_size,
            )
            return 0, 0
        else:
            return int(width_str), int(height_str)

    def string_to_datetime(self) -> datetime | None:
        if not self.date_str or self.date_str == "0000:00:00 00:00:00":
            return None

        # Standardize EXIF colons (2026:06:24 14:00:00 -> 2026-06-24 14:00:00)
        match: Match[str] | None = EXIF_DATE_PATTERN.match(self.date_str)
        if match:
            # Replace only the colons separating YYYY, MM, and DD
            normalized_date = f"{match.group(1)}-{match.group(2)}-{match.group(3)}{self.date_str[10:]}"
        else:
            normalized_date = self.date_str

        # Safely parse date string
        try:
            return dateutil.parser.parse(normalized_date)
        except (ValueError, TypeError) as e:
            logger.warning("  - Failed to parse date string '%s': %s", self.date_str, e)
            return None

    def render_path(self, path) -> str:
        return path.format(year=self.year, month=self.month, day=self.day)

    @property
    def year(self) -> str | None:
        return f"{self.date.year:04d}" if self.date is not None else None

    @property
    def month(self) -> str | None:
        return f"{self.date.month:02d}" if self.date is not None else None

    @property
    def day(self) -> str | None:
        return f"{self.date.day:02d}" if self.date is not None else None
