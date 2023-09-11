"""Tools for export with images."""

from pathlib import Path
from typing import Dict, Tuple

from PIL import Image

from kili.services.export.exceptions import NotExportableAssetError


def _get_image_dimensions(filepath: str) -> Tuple:
    """Get an image width and height."""
    image = Image.open(filepath)
    return image.size


def get_image_dimensions(asset: Dict) -> Tuple:
    """Get an asset image width and height."""
    if "resolution" in asset and asset["resolution"] is not None:
        return (asset["resolution"]["width"], asset["resolution"]["height"])

    if Path(asset["content"]).is_file():
        return _get_image_dimensions(asset["content"])

    raise NotExportableAssetError(
        f"Could not find dimensions for asset with externalId '{asset['externalId']}'. Please"
        " use `kili.update_properties_in_assets()` to update the resolution of your asset. Or use"
        " `kili.export_labels(with_assets=True).`"
    )


def get_frame_dimensions(asset: Dict) -> Tuple:
    """Get a video asset frame width and height."""
    if "resolution" in asset and asset["resolution"] is not None:
        return (asset["resolution"]["width"], asset["resolution"]["height"])

    if (
        isinstance(asset["jsonContent"], list)
        and len(asset["jsonContent"]) > 0
        and Path(asset["jsonContent"][0]).is_file()
    ):
        return _get_image_dimensions(asset["jsonContent"][0])

    raise NotExportableAssetError(
        f"Could not find dimensions for asset with externalId '{asset['externalId']}'. Please"
        " use `kili.update_properties_in_assets()` to update the resolution of your asset. Or use"
        " `kili.export_labels(with_assets=True).`"
    )
