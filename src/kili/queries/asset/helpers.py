"""Helpers for the asset queries"""

from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from mimetypes import guess_extension
from pathlib import Path
from typing import Callable, List, Optional

import requests
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_random

from kili.queries.asset.exceptions import MissingPropertyError


def get_post_assets_call_process(
    download_media: bool, local_media_dir: Optional[str], project_id: str
) -> Callable:
    """
    Define the function to apply on assets after a paginated call of assets
    Call the download_asset_media with the right parameters if download_media is True
    Otherwise return assets without any post-processing
    """
    if download_media:
        local_dir_path = (
            Path(local_media_dir)
            if local_media_dir is not None
            else Path.home() / ".cache" / "kili" / "projects" / project_id / "assets"
        )
        return lambda assets: download_asset_content(assets, local_dir_path)

    return lambda assets: assets


def get_file_extension_from_headers(url) -> Optional[str]:
    """guess the extension of a file with the url response headers"""
    with requests.head(url, timeout=20) as header_response:
        if header_response.status_code == 200:
            headers = header_response.headers
        else:
            with requests.get(url, timeout=20) as response:
                response.raise_for_status()
                headers = response.headers
        content_type = headers["content-type"]
        return guess_extension(content_type)


def get_download_path(url: str, external_id: str, local_dir_path: Path) -> Path:
    """Build the path to download a file the file in local."""
    local_path = local_dir_path / external_id
    extension = get_file_extension_from_headers(url)
    if extension is not None:
        local_path = local_path.with_suffix(extension)
    return local_path.resolve()


@retry(stop=stop_after_attempt(2), wait=wait_random(min=1, max=2))
def download_file(url: str, external_id: str, local_dir_path: Path) -> Path:
    """
    Download a file by streming chunks of 1Mb
    If the file already exists in local, it does not download it
    """
    local_path = get_download_path(url, external_id, local_dir_path)
    if not local_path.is_file():
        with requests.get(url, stream=True, timeout=20) as response:
            response.raise_for_status()
            with open(local_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    file.write(chunk)
    return local_path


def assert_required_fields_existence(asset: dict) -> None:
    """Get a list of an asset field from a generator of kili assets"""
    required_fields = ["content", "externalId"]
    for field in required_fields:
        if field not in asset.keys():
            raise MissingPropertyError(
                f"The asset does not have the {field} field. Please add it to the fields when"
                " querying assets "
            )
        content = asset["content"]
        if content == "":
            raise NotImplementedError(
                "The media of the asset is not stored in the content field. If your asset is video"
                " imported from frames or a richText asset, the media is stored in the jsonContent"
                " field. The download in local of such asset media is currently not supported."
            )


def download_asset_content(assets: List[dict], local_dir_path: Path) -> List[dict]:
    """Download assets media in local."""
    if len(assets) == 0:
        return assets
    local_dir_path.mkdir(parents=True, exist_ok=True)
    assert_required_fields_existence(assets[0])
    content_gen = (asset["content"] for asset in assets)
    external_id_gen = (asset["externalId"] for asset in assets)
    with ThreadPoolExecutor() as threads:
        path_gen = threads.map(download_file, content_gen, external_id_gen, repeat(local_dir_path))
    return [{**asset, "content": str(path)} for asset, path in zip(assets, path_gen)]
