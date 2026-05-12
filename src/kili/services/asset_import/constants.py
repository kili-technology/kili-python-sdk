"""Constants for the asset_import services."""

from kili.core.constants import MIME_EXTENSIONS_FOR_IV2

project_compatible_mimetypes = MIME_EXTENSIONS_FOR_IV2

IMPORT_BATCH_SIZE = 100
FRAME_IMPORT_BATCH_SIZE = 1

MB_SIZE = 1024**2
LARGE_IMAGE_THRESHOLD_SIZE = 30 * MB_SIZE
MAX_WIDTH_OR_HEIGHT_NON_TILED = 10000

ALLOWED_EXTENSIONS_BY_INPUT_TYPE: dict[str, frozenset[str]] = {
    "AUDIO": frozenset({".flac", ".mp3", ".mp4", ".wav"}),
    "GEOSPATIAL": frozenset({".tif", ".tiff", ".jp2", ".ntf", ".nitf"}),
    "IMAGE": frozenset(
        {
            ".jpeg",
            ".jpg",
            ".png",
            ".bmp",
            ".gif",
            ".webp",
            ".ico",
            ".tif",
            ".tiff",
            ".jp2",
            ".ntf",
            ".nitf",
        }
    ),
    "LLM_RLHF": frozenset({".json"}),
    "PDF": frozenset({".pdf"}),
    "TEXT": frozenset({".txt", ".csv"}),
    "VIDEO": frozenset({".mp4", ".mkv", ".3gp", ".avi", ".m4v", ".mov", ".webm"}),
}
