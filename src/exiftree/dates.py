from datetime import datetime
import dateutil


class MediaDate:
    def __init__(self, dateStr) -> None:
        self.dateStr = dateStr
        self.date: datetime | None = self.string_to_datetime()

    def string_to_datetime(self) -> datetime | None:
        if self.dateStr is None or self.dateStr == "0000:00:00 00:00:00":
            return None

        # Standardize EXIF colons (2026:06:24 -> 2026-06-24)
        if self.dateStr[4] == ":" and self.dateStr[7] == ":":
            self.dateStr = self.dateStr[:4] + "-" + self.dateStr[5:7] + "-" + self.dateStr[8:]

        # Returns a standard Python datetime object
        return dateutil.parser.parse(self.dateStr)

    @property
    def YYYY(self):
        return f"{self.date.year:04d}" if self.date is not None else None

    @property
    def MM(self):
        return f"{self.date.month:02d}" if self.date is not None else None

    @property
    def DD(self):
        return f"{self.date.day:02d}" if self.date is not None else None
