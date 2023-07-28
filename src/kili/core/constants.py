"""This script lists package constants."""


NO_ACCESS_RIGHT = (
    "[noAccessRights] It seems you do not have access to this object."
    " Please double check your credentials."
)

INPUT_TYPE = [
    "AUDIO",
    "IMAGE",
    "PDF",
    "TEXT",
    "TIME_SERIES",
    "VIDEO",
    "VIDEO_LEGACY",
]

mime_extensions = {
    "Audio": "audio/x-flac,audio/mpeg,video/mp4",
    "Csv": "text/csv",
    "Video": (
        "video/mp4,video/x-matroska,video/3gpp,video/x-msvideo,"
        "video/x-m4v,video/quicktime,video/webm"
    ),
    "Image": (
        "image/jpeg,image/png,image/bmp,image/gif,image/webp,image/x-icon,"
        "image/tiff,image/vnd.microsoft.icon,image/svg+xml,image/avif,image/apng"
    ),
    "Pdf": "application/pdf",
    "Text": "text/plain",
    "TimeSeries": "text/csv",
}

mime_extensions_for_IV2 = {
    "AUDIO": mime_extensions["Audio"],
    "IMAGE": mime_extensions["Image"],
    "NA": "",
    "PDF": mime_extensions["Pdf"],
    "TEXT": mime_extensions["Text"],
    "TIME_SERIES": mime_extensions["Csv"],
    "URL": "",
    "VIDEO": mime_extensions["Video"],
    "VIDEO_LEGACY": mime_extensions["Csv"],
}

mime_extensions_for_py_scripts = ["text/x-python"]
mime_extensions_for_txt_files = ["text/plain"]

QUERY_BATCH_SIZE = 100
MUTATION_BATCH_SIZE = 100
MAX_CALLS_PER_MINUTE = 500
