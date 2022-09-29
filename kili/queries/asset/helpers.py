"""Helpers for the asset queries"""

from pathlib import Path
from typing import Optional

from kili.services.asset_download import download_asset_media


def get_post_assets_call_process(
    download_media: bool, local_media_dir: Optional[str], project_id: str
):
    """
    Define the function to apply on assets after a paginated call of assets
    Call the download_asset_media with the right parameters if download_media is True
    Otherwise return assets without any post-processing
    """
    if download_media:
        local_dir_path = (
            Path(local_media_dir)
            if local_media_dir is not None
            else Path(f".cache/kili/projects/{project_id}/assets")
        )

        return lambda assets: download_asset_media(assets, local_dir_path)

    else:
        return lambda assets: assets
