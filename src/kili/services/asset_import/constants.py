"""
Constants for the asset_improt services
"""

from uuid import uuid4

from .types import AssetLike

ASSET_FIELDS_DEFAULT_VALUE = AssetLike(
    content="",
    json_content="",
    external_id=uuid4().hex,
    status="TODO",
    json_metadata="{}",
    is_honeypot=False,
    id="",
)

mime_extensions = {
    "Audio": "audio/x-flac,audio/mpeg,video/mp4",
    "Csv": "text/csv",
    "Video": "video/mp4,video/x-matroska,video/3gpp,video/x-msvideo,"
    "video/x-m4v,video/quicktime,video/webm",
    "Image": "image/jpeg,image/png,image/bmp,image/gif,image/webp,image/x-icon,"
    "image/tiff,image/vnd.microsoft.icon,image/svg+xml,image/avif,image/apng",
    "Pdf": "application/pdf",
    "Text": "text/plain",
    "TimeSeries": "text/csv",
}

project_compatible_mimetypes = {
    "AUDIO": mime_extensions["Audio"],
    "FRAME": mime_extensions["Video"],
    "IMAGE": mime_extensions["Image"],
    "NA": "",
    "PDF": mime_extensions["Pdf"],
    "TEXT": mime_extensions["Text"],
    "TIME_SERIES": mime_extensions["Csv"],
    "URL": "",
    "VIDEO": mime_extensions["Video"],
    "VIDEO_LEGACY": mime_extensions["Csv"],
}

IMPORT_BATCH_SIZE = 10
FRAME_IMPORT_BATCH_SIZE = 1

MB_SIZE = 1024**2
LARGE_IMAGE_THRESHOLD_SIZE = 30 * MB_SIZE
