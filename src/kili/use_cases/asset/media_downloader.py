"""Helpers for the asset queries."""

import warnings
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from mimetypes import guess_extension
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union

from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_random

from kili.adapters.http_client import HttpClient
from kili.domain.asset import AssetExternalId
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.use_cases.asset.exceptions import (
    DownloadNotAllowedError,
    MissingPropertyError,
)

if TYPE_CHECKING:
    from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway


def get_download_assets_function(
    kili_api_gateway: "KiliAPIGateway",
    download_media: bool,
    fields: ListOrTuple[str],
    project_id: ProjectId,
    local_media_dir: Optional[str],
) -> Tuple[Optional[Callable], ListOrTuple[str]]:
    """Get the function to be called after each batch of asset query.

    The function is either None or MediaDownloader.download_assets().

    Also returns the fields to be queried, which may be modified
    if the jsonContent field is necessary.
    """
    if not download_media:
        return None, fields

    project = kili_api_gateway.get_project(
        project_id=project_id, fields=("inputType", "dataConnections.id")
    )
    input_type = project["inputType"]

    # We need to query the data connections to know if the assets are hosted in a cloud storage
    # If so, we remove the fields "content" and "jsonContent" from the query
    if project["dataConnections"]:
        raise DownloadNotAllowedError(
            "The download of assets from a project connected to a cloud storage is not allowed."
            " Asset download is disabled."
        )

    jsoncontent_field_added = False
    if input_type in ("TEXT", "VIDEO") and "jsonContent" not in fields:
        fields = ("jsonContent", *fields)
        jsoncontent_field_added = True

    return (
        MediaDownloader(
            local_media_dir,
            project_id,
            jsoncontent_field_added,
            input_type,
            kili_api_gateway.http_client,
        ).download_assets,
        fields,
    )


class MediaDownloader:
    """Media downloader for kili.assets()."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        local_media_dir: Optional[Union[Path, str]],
        project_id: str,
        jsoncontent_field_added: bool,
        project_input_type: str,
        http_client: HttpClient,
    ) -> None:
        self.local_media_dir = local_media_dir
        self.project_id = project_id
        self.jsoncontent_field_added = jsoncontent_field_added
        self.project_input_type = project_input_type
        self.http_client = http_client

        self.local_dir_path = (
            Path(self.local_media_dir)
            if self.local_media_dir is not None
            else Path.home() / ".cache" / "kili" / "projects" / self.project_id / "assets"
        )

    def download_assets(self, assets: List[Dict]) -> List[Dict]:
        """Download assets media in local."""
        if len(assets) == 0:
            return assets

        assert_required_fields_existence(assets)

        self.local_dir_path.mkdir(parents=True, exist_ok=True)

        with ThreadPoolExecutor() as threads:
            assets_gen = threads.map(self.download_single_asset, assets)

        assets = list(assets_gen)

        if self.jsoncontent_field_added:
            jsoncontent_not_empty = any(bool(asset["jsonContent"]) for asset in assets)
            if jsoncontent_not_empty:
                warnings.warn(
                    "Non empty jsonContent found in assets. Field was automatically added.",
                    stacklevel=2,
                )
            else:
                for asset in assets:
                    del asset["jsonContent"]

        return assets

    def download_single_asset(self, asset: Dict) -> Dict[str, Any]:
        """Download single asset on disk and modify asset attributes."""
        if "ocrMetadata" in asset and str(asset["ocrMetadata"]).startswith("http"):
            response = self.http_client.get(asset["ocrMetadata"], timeout=20).json()
            asset["ocrMetadata"] = response

        if "jsonContent" in asset and str(asset["jsonContent"]).startswith("http"):
            # richtext
            if self.project_input_type == "TEXT":
                asset["jsonContent"] = download_file(
                    asset["jsonContent"], asset["externalId"], self.local_dir_path, self.http_client
                )

            # video frames
            elif self.project_input_type == "VIDEO":
                response = self.http_client.get(asset["jsonContent"], timeout=20).json()
                urls = tuple(response.values())
                nbr_char_zfill = len(str(len(urls)))
                img_names = (
                    f'{asset["externalId"]}_{f"{i+1}".zfill(nbr_char_zfill)}'
                    for i, _ in enumerate(urls)
                )
                with ThreadPoolExecutor() as threads:
                    paths_gen = threads.map(
                        download_file,
                        urls,
                        img_names,
                        repeat(self.local_dir_path),
                        repeat(self.http_client),
                    )
                    asset["jsonContent"] = list(paths_gen)
                return asset  # we skip video "content" download

            # big images
            elif self.project_input_type == "IMAGE":
                # the "jsonContent" contains some information but not the image
                response = self.http_client.get(asset["jsonContent"], timeout=20).json()
                asset["jsonContent"] = response

            else:
                raise NotImplementedError(
                    f"jsonContent download for type {self.project_input_type} not implemented yet."
                )

        if str(asset["content"]).startswith("http"):
            asset["content"] = download_file(
                asset["content"], asset["externalId"], self.local_dir_path, self.http_client
            )
            return asset

        return asset


def get_file_extension_from_headers(url: str, http_client: HttpClient) -> Optional[str]:
    """Guess the extension of a file with the url response headers."""
    with http_client.head(url, timeout=20) as header_response:
        if header_response.status_code == 200:
            headers = header_response.headers
        else:
            with http_client.get(url, timeout=20) as response:
                response.raise_for_status()
                headers = response.headers
        if "content-type" in headers:
            content_type = headers["content-type"].split(";")[0]
            # (#ML-1368) remove parameters the content-type to only get
            # the mimetype in the type/subtype format
            return guess_extension(content_type)
    return None


def get_download_path(
    url: str, external_id: AssetExternalId, local_dir_path: Path, http_client: HttpClient
) -> Path:
    """Build the path to download a file the file in local."""
    extension = get_file_extension_from_headers(url, http_client)
    filename = external_id
    if extension is not None and not filename.endswith(extension):
        filename = filename + extension
    local_dir_path = local_dir_path / filename
    return local_dir_path.resolve()


@retry(stop=stop_after_attempt(2), wait=wait_random(min=1, max=2), reraise=True)
def download_file(
    url: str, external_id: AssetExternalId, local_dir_path: Path, http_client: HttpClient
) -> str:
    """Download a file by streming chunks of 1Mb.

    If the file already exists in local, it does not download it.
    """
    local_path = get_download_path(url, external_id, local_dir_path, http_client)
    local_path.parent.mkdir(parents=True, exist_ok=True)
    if not local_path.is_file():
        with http_client.get(url, stream=True, timeout=20) as response:
            response.raise_for_status()
            with local_path.open("wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    file.write(chunk)
    return str(local_path)


def assert_required_fields_existence(assets: List[Dict]) -> None:
    """Check if all fields are available to download assets."""
    required_fields = ["content", "externalId"]
    for field in required_fields:
        if field not in assets[0]:
            raise MissingPropertyError(
                f"The asset does not have the {field} field. Please add it to the fields when"
                " querying assets."
            )
