from datetime import datetime
import os

import dateutil.parser
import exiftool


def string_to_datetime(raw_date_string) -> datetime | None:

    # + filter impossible dates
    if raw_date_string is None:
        return None

    # Standardize EXIF colons (2026:06:24 -> 2026-06-24)
    if raw_date_string[4] == ":" and raw_date_string[7] == ":":
        raw_date_string = raw_date_string[:4] + "-" + raw_date_string[5:7] + "-" + raw_date_string[8:]

    # Returns a standard Python datetime object
    return dateutil.parser.parse(raw_date_string)


def define_output(files_path, base_path, template) -> dict[str, str]:

    # Get file metadatas
    with exiftool.ExifToolHelper() as et:
        files_metadatas = et.get_metadata(files=files_path)

    output: dict[str, str] = {}
    for f in files_metadatas:
        file: str = f.get("SourceFile")
        imageSize: str = f.get("Composite:ImageSize")

        quickTimeDate: datetime | None = string_to_datetime(f.get("QuickTime:CreateDate"))
        exifDate: datetime | None = string_to_datetime(f.get("EXIF:DateTimeOriginal"))
        fileDate = None
        if quickTimeDate:
            fileDate = quickTimeDate
        elif exifDate:
            fileDate = exifDate

        if fileDate is not None:
            YYYY: str = f"{fileDate.year:04d}"
            MM: str = f"{fileDate.month:02d}"
            DD: str = f"{fileDate.day:02d}"

            output[file] = os.path.join(base_path, template.format(YYYY=YYYY, MM=MM, DD=DD))
        else:
            output[file] = os.path.join(base_path, "Unknown")
    return output
