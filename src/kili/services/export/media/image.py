"""Tools for export with images."""

from pathlib import Path
from typing import Dict, Tuple

from PIL import Image

from ..exceptions import NotExportableAssetError


def get_image_dimensions(asset: Dict) -> Tuple:
    """Get an asset image width and height."""
    if "resolution" in asset and asset["resolution"] is not None:
        return (asset["resolution"]["width"], asset["resolution"]["height"])

    if Path(asset["content"]).is_file():
        image = Image.open(str(asset["content"]))
        return image.size

    # video with frames
    if (
        isinstance(asset["jsonContent"], list)
        and len(asset["jsonContent"]) > 0
        and Path(asset["jsonContent"][0]).is_file()
    ):
        image = Image.open(str(asset["jsonContent"][0]))
        return image.size

    raise NotExportableAssetError(
        f"Could not find image dimensions for asset with externalId '{asset['externalId']}'. Please"
        " use `kili.update_properties_in_assets()` to update the resolution of your asset. Or use"
        " `kili.export_labels(with_assets=True).`"
    )
