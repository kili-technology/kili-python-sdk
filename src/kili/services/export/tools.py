"""
Set of common functions used by different export formats
"""
from typing import Dict, List, Optional

from kili.authentication import KiliAuth
from kili.graphql import QueryOptions
from kili.graphql.operations.asset.queries import AssetQuery, AssetWhere
from kili.queries.asset.media_downloader import get_download_assets_function
from kili.services.export.exceptions import NotExportableAssetError
from kili.services.export.types import ExportType

DEFAULT_FIELDS = [
    "id",
    "content",
    "externalId",
    "jsonMetadata",
    "labels.author.id",
    "labels.author.email",
    "labels.author.firstname",
    "labels.author.lastname",
    "labels.jsonResponse",
    "labels.createdAt",
    "labels.isLatestLabelForUser",
    "labels.labelType",
    "labels.modelName",
]
LATEST_LABEL_FIELDS = [
    "id",
    "content",
    "externalId",
    "jsonContent",
    "jsonMetadata",
    "latestLabel.author.id",
    "latestLabel.author.email",
    "latestLabel.jsonResponse",
    "latestLabel.author.firstname",
    "latestLabel.author.lastname",
    "latestLabel.createdAt",
    "latestLabel.isLatestLabelForUser",
    "latestLabel.labelType",
    "latestLabel.modelName",
]


def attach_name_to_assets_labels_author(assets: List[Dict], export_type: ExportType):
    """
    Adds `name` field for author, by concatenating his/her first and last name
    """
    for asset in assets:
        if export_type == "latest":
            latest_label = asset["latestLabel"]
            if latest_label:
                firstname = latest_label["author"]["firstname"]
                lastname = latest_label["author"]["lastname"]
                latest_label["author"]["name"] = f"{firstname} {lastname}"
            continue
        for label in asset.get("labels", []):
            firstname = label["author"]["firstname"]
            lastname = label["author"]["lastname"]
            label["author"]["name"] = f"{firstname} {lastname}"


def fetch_assets(  # pylint: disable=too-many-arguments
    auth: KiliAuth,
    project_id: str,
    asset_ids: Optional[List[str]],
    export_type,
    label_type_in=None,
    disable_tqdm: bool = False,
    download_media: bool = False,
    local_media_dir: Optional[str] = None,
):
    """Fetches assets.

    Fetches assets where ID are in asset_ids if the list has more than one element,
    else all the assets of the project. If download media is passed, the media are
    downloaded into the `$HOME/.cache` folder.

    Args:
        project_id: project id
        assets_ids: list of asset IDs
        export_type: type of export (latest label or all labels)
        label_type_in: types of label to fetch (default, reviewed, ...)
        disable_tqdm: tell to disable tqdm
        download_media: tell to download the media in the cache folder.
        local_media_dir: Directory where the media are downloaded if `download_media` is True.

    Returns:
        List of fetched assets.
    """

    fields = get_fields_to_fetch(export_type)
    assets = None

    if asset_ids is not None and len(asset_ids) > 0:
        where = AssetWhere(
            asset_id_in=asset_ids,
            project_id=project_id,
            label_type_in=label_type_in,
        )
    else:
        where = AssetWhere(
            project_id=project_id,
            label_type_in=label_type_in,
        )
    options = QueryOptions(disable_tqdm=disable_tqdm)
    post_call_function, fields = get_download_assets_function(
        auth, download_media, fields, project_id, local_media_dir
    )
    assets = list(
        AssetQuery(auth.client, auth.ssl_verify)(where, fields, options, post_call_function)
    )
    _check_content_presence(assets)
    attach_name_to_assets_labels_author(assets, export_type)
    return assets


def _check_content_presence(assets: List[Dict]):
    if any(a.get("content") in [None, ""] and a.get("jsonContent") in [None, ""] for a in assets):
        raise NotExportableAssetError(
            "The assets cannot be exported. This can happen if they are hosted in a cloud storage."
        )


def get_fields_to_fetch(export_type: ExportType):
    """
    Returns the fields to fetch depending on the export type
    """
    if export_type == "latest":
        return LATEST_LABEL_FIELDS
    return DEFAULT_FIELDS
