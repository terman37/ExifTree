from datetime import datetime
import logging
import re
import dateutil.parser

logger = logging.getLogger(__name__)

# Pattern to identify traditional EXIF date representation (e.g., "YYYY:MM:DD HH:MM:SS")
EXIF_DATE_PATTERN = re.compile(r"^(\d{4}):(\d{2}):(\d{2})")


class MediaDate:
    def __init__(self, date_str: str | None) -> None:
        self.date_str: str | None = date_str
        self.date: datetime | None = self.string_to_datetime()

    def string_to_datetime(self) -> datetime | None:
        if not self.date_str or self.date_str == "0000:00:00 00:00:00":
            return None

        # Standardize EXIF colons (2026:06:24 14:00:00 -> 2026-06-24 14:00:00)
        match = EXIF_DATE_PATTERN.match(self.date_str)
        if match:
            # Replace only the colons separating YYYY, MM, and DD
            normalized_date = f"{match.group(1)}-{match.group(2)}-{match.group(3)}{self.date_str[10:]}"
        else:
            normalized_date = self.date_str

        # Safely parse date string
        try:
            return dateutil.parser.parse(normalized_date)
        except (ValueError, TypeError) as e:
            logger.warning("Failed to parse date string '%s': %s", self.date_str, e)
            return None

    @property
    def year(self) -> str | None:
        return f"{self.date.year:04d}" if self.date is not None else None

    @property
    def month(self) -> str | None:
        return f"{self.date.month:02d}" if self.date is not None else None

    @property
    def day(self) -> str | None:
        return f"{self.date.day:02d}" if self.date is not None else None
