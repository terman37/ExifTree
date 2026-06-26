from datetime import datetime
import os

import dateutil.parser
import exiftool

from exiftree.dates import MediaDate


def define_output(files_path, base_path, template) -> dict[str, str]:

    # Get file metadatas
    with exiftool.ExifToolHelper() as et:
        files_metadatas = et.get_metadata(files=files_path)

    output: dict[str, str] = {}
    for f in files_metadatas:
        file: str = f.get("SourceFile")
        imageSize: str = f.get("Composite:ImageSize")

        quickTimeDate = f.get("QuickTime:CreateDate")
        exifDate = f.get("EXIF:DateTimeOriginal")

        if quickTimeDate:
            fileDate = quickTimeDate
        elif exifDate:
            fileDate = exifDate
        else:
            fileDate = None

        MediaFile: MediaDate = MediaDate(dateStr=fileDate)
        if MediaFile.date:
            output[file] = os.path.join(base_path, template.format(YYYY=MediaFile.YYYY, MM=MediaFile.MM, DD=MediaFile.DD))
        else:
            output[file] = os.path.join(base_path, "Unknown")

        output[file] = os.path.join(output[file], os.path.basename(file))

    return output
