from typing import Literal


from datetime import datetime
from logging import Logger
import logging
import os
from re import Match, Pattern
import re

import dateutil.parser
from pydantic import BaseModel, Field

logger: Logger = logging.getLogger(name=__name__)

# Pattern to identify traditional EXIF date representation (e.g., "YYYY:MM:DD HH:MM:SS")
EXIF_DATE_PATTERN: Pattern[str] = re.compile(r"^(\d{4}):(\d{2}):(\d{2})")

# Pattern to find a date in a file name (e.g., "2026-06-24", "20260624", "2026_06_24")
FILENAME_DATE_PATTERN: Pattern[str] = re.compile(r"(?<!\d)(\d{4})[-_.]?(\d{2})[-_.]?(\d{2})(?!\d)")

# Extensions whose date tag lives in QuickTime metadata rather than EXIF
VIDEO_EXTENSIONS: set[str] = {
    "mp4", "mov", "m4v", "mpg", "mpeg", "wmv", "avi", "3gp",
    "mkv", "webm", "mts", "m2ts", "ts",
}


class FileMetadata(BaseModel):
    source_file: str = Field(alias="SourceFile")
    image_size: str | None = Field(default=None, alias="Composite:ImageSize")
    quicktime_create_date: str | None = Field(default=None, alias="QuickTime:CreateDate")
    exif_datetime_original: str | None = Field(default=None, alias="EXIF:DateTimeOriginal")


class Media:

    def __init__(self, raw_metadata) -> None:

        # Validate raw dictionaries into structured models
        metadata: FileMetadata = FileMetadata.model_validate(raw_metadata)

        self.date_from_filename: bool = False  # set by find_date
        self.date_str: str | None = self.find_date(metadata)
        self.date: datetime | None = self.string_to_datetime()
        self.file = metadata.source_file
        self.extension: str = os.path.splitext(metadata.source_file)[1].lstrip(".").lower()
        self.width, self.height = self.get_size(metadata.image_size)

    def find_date(self, metadata) -> str | None:
        self.date_from_filename = False
        for candidate in (metadata.quicktime_create_date, metadata.exif_datetime_original):
            if candidate and candidate != "0000:00:00 00:00:00":
                return candidate
        file_date: str | None = self.find_date_in_filename(metadata.source_file)
        if file_date:
            self.date_from_filename = True
        return file_date

    def find_date_in_filename(self, file_path: str) -> str | None:
        """Extract a date from the file name when metadata carries none."""
        file_name: str = os.path.basename(file_path)
        today = datetime.now().date()
        for match in FILENAME_DATE_PATTERN.finditer(file_name):
            try:
                date = datetime(
                    year=int(match.group(1)),
                    month=int(match.group(2)),
                    day=int(match.group(3)),
                ).date()
            except ValueError:
                continue  # e.g., month 13 or day 99: not a valid date
            if date.year < 1979 or date > today:
                continue  # not a plausible capture date
            return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        return None

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

    @property
    def write_tags(self) -> dict[str, str] | None:
        """Tags to inject into the file when the date came from its name only."""
        if not self.date_from_filename or self.date is None:
            return None
        if self.extension in VIDEO_EXTENSIONS:
            return {"QuickTime:CreateDate": self.date.strftime("%Y-%m-%d %H:%M:%S")}
        return {"EXIF:DateTimeOriginal": self.date.strftime("%Y:%m:%d %H:%M:%S")}

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
