"""Constants for the asset_import services."""

from kili.core.constants import mime_extensions_for_IV2

project_compatible_mimetypes = mime_extensions_for_IV2

IMPORT_BATCH_SIZE = 100
FRAME_IMPORT_BATCH_SIZE = 1

MB_SIZE = 1024**2
LARGE_IMAGE_THRESHOLD_SIZE = 30 * MB_SIZE
