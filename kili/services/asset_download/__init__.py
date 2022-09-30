"""
Service for downloading assets media in local
"""

from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from mimetypes import guess_extension
from pathlib import Path
from typing import List

import requests
from kili.services.asset_download.exceptions import MissingPropertyError
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_random


@retry(stop=stop_after_attempt(2), wait=wait_random(min=1, max=2))
def download_file(url: str, external_id: str, local_dir_path: Path):
    """Download a file by streming chunks of 1Mb"""
    with requests.get(url, stream=True, timeout=20) as response:
        response.raise_for_status()
        content_type = response.headers["content-type"]
        extension = guess_extension(content_type)
        local_path = local_dir_path / external_id
        if extension is not None:
            local_path = local_path.with_suffix(extension)
        with open(local_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                file.write(chunk)
    return local_path


def get_field_array(assets: List[dict], field: str):
    """Get a list of an asset field from a generator of kili assets"""
    field_array = []
    for asset in assets:
        value = asset.get(field)
        if value is None:
            raise MissingPropertyError(
                f"The asset does not have the {field} property. Please add it to the fields when"
                " querying assets "
            )
        field_array.append(value)
    return field_array


def download_asset_media(assets: List[dict], local_dir_path: Path) -> List[dict]:
    """Download assets media in local"""
    local_dir_path.mkdir(parents=True, exist_ok=True)
    content_array: List[str] = get_field_array(assets, "content")
    external_id_array: List[str] = get_field_array(assets, "externalId")
    with ThreadPoolExecutor() as threads:
        path_gen = threads.map(
            download_file, content_array, external_id_array, repeat(local_dir_path)
        )
    return [{**asset, "content": str(path)} for asset, path in zip(assets, path_gen)]
