"""Tests for how image assets are routed between the sync and async importers.

`split_asset_by_upload_type` decides whether an asset is uploaded directly or
handed to the backend for post-processing. Nothing covered it, and it is the
code that changed when image measuring moved off Pillow, so it is pinned here.
"""

from pathlib import Path

from kili.services.asset_import.constants import (
    LARGE_IMAGE_THRESHOLD_SIZE,
    MAX_WIDTH_OR_HEIGHT_NON_TILED,
)
from kili.services.asset_import.image import ImageDataImporter

ASSETS = Path(__file__).parent / "assets"


def _split(paths):
    assets = [{"content": str(path), "external_id": Path(path).name} for path in paths]
    sync_assets, async_assets = ImageDataImporter.split_asset_by_upload_type(
        assets, is_hosted=False
    )
    return [asset["external_id"] for asset in sync_assets], [
        asset["external_id"] for asset in async_assets
    ]


def test_a_small_image_is_uploaded_synchronously():
    sync_assets, async_assets = _split([ASSETS / "smoke.jpg"])

    assert sync_assets == ["smoke.jpg"]
    assert async_assets == []


def test_a_tiff_always_goes_to_post_processing():
    """TIFF needs backend post-processing, so it never reaches the measuring code."""
    sync_assets, async_assets = _split([ASSETS / "smoke.tiff"])

    assert sync_assets == []
    assert async_assets == ["smoke.tiff"]


def test_an_unreadable_file_goes_to_post_processing(tmp_path):
    """A file we cannot measure is handed to the backend rather than refused.

    This used to rely on PIL's `UnidentifiedImageError`; it now relies on the
    kili-formats one. The routing must not change.
    """
    not_an_image = tmp_path / "broken.png"
    not_an_image.write_text("certainly not a PNG", encoding="utf-8")

    sync_assets, async_assets = _split([not_an_image])

    assert sync_assets == []
    assert async_assets == ["broken.png"]


def test_a_small_image_is_not_considered_large():
    assert ImageDataImporter.get_is_large_image(str(ASSETS / "smoke.jpg")) is False


def test_a_heavy_file_is_considered_large(tmp_path):
    """Past the size threshold the file is tiled without being measured at all."""
    heavy = tmp_path / "heavy.jpg"
    heavy.write_bytes((ASSETS / "smoke.jpg").read_bytes())
    with heavy.open("ab") as file:
        file.write(b"\0" * LARGE_IMAGE_THRESHOLD_SIZE)

    assert ImageDataImporter.get_is_large_image(str(heavy)) is True


def test_a_wide_image_is_considered_large(tmp_path):
    """Past the dimension threshold the image is tiled.

    The PNG is written by hand so the test stays independent of any encoder.
    """
    import struct
    import zlib

    width, height = MAX_WIDTH_OR_HEIGHT_NON_TILED, 10

    def chunk(kind, payload):
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload))
        )

    raw = b"".join(b"\0" + b"\0\0\0" * width for _ in range(height))
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )
    wide = tmp_path / "wide.png"
    wide.write_bytes(png)

    assert wide.stat().st_size < LARGE_IMAGE_THRESHOLD_SIZE
    assert ImageDataImporter.get_is_large_image(str(wide)) is True
