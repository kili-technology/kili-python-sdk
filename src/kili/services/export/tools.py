"""Set of common functions used by different export formats."""
from typing import Dict, List, Optional

from kili.core.authentication import KiliAuth
from kili.core.graphql import QueryOptions
from kili.core.graphql.operations.asset.queries import AssetQuery, AssetWhere
from kili.core.helpers import validate_category_search_query
from kili.entrypoints.queries.asset.media_downloader import get_download_assets_function
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
    """Adds `name` field for author, by concatenating his/her first and last name."""
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
    export_type: ExportType,
    label_type_in: Optional[List[str]] = None,
    disable_tqdm: bool = False,
    download_media: bool = False,
    local_media_dir: Optional[str] = None,
    asset_filter_kwargs: Optional[Dict[str, object]] = None,
) -> List[Dict]:
    """Fetches assets.

    Fetches assets where ID are in asset_ids if the list has more than one element,
    else all the assets of the project. If download media is passed, the media are
    downloaded into the `$HOME/.cache` folder.

    Args:
        auth: Kili authentication object
        project_id: project id
        asset_ids: list of asset IDs
        export_type: type of export (latest label or all labels)
        label_type_in: types of label to fetch (default, reviewed, ...)
        disable_tqdm: tell to disable tqdm
        download_media: tell to download the media in the cache folder.
        local_media_dir: Directory where the media are downloaded if `download_media` is True.
        asset_filter_kwargs: Optional dictionary of arguments to filter the assets to export.

    Returns:
        List of fetched assets.
    """
    fields = get_fields_to_fetch(export_type)

    asset_filter_kwargs = asset_filter_kwargs or {}
    asset_where_params = {
        "project_id": project_id,
        "label_type_in": label_type_in,
        "consensus_mark_gte": asset_filter_kwargs.pop("consensus_mark_gte", None),
        "consensus_mark_lte": asset_filter_kwargs.pop("consensus_mark_lte", None),
        "external_id_contains": asset_filter_kwargs.pop("external_id_contains", None),
        "honeypot_mark_gte": asset_filter_kwargs.pop("honeypot_mark_gte", None),
        "honeypot_mark_lte": asset_filter_kwargs.pop("honeypot_mark_lte", None),
        "label_author_in": asset_filter_kwargs.pop("label_author_in", None),
        "label_reviewer_in": asset_filter_kwargs.pop("label_reviewer_in", None),
        "skipped": asset_filter_kwargs.pop("skipped", None),
        "status_in": asset_filter_kwargs.pop("status_in", None),
        "label_category_search": asset_filter_kwargs.pop("label_category_search", None),
        "created_at_gte": asset_filter_kwargs.pop("created_at_gte", None),
        "created_at_lte": asset_filter_kwargs.pop("created_at_lte", None),
        "issue_type": asset_filter_kwargs.pop("issue_type", None),
        "issue_status": asset_filter_kwargs.pop("issue_status", None),
        "inference_mark_gte": asset_filter_kwargs.pop("inference_mark_gte", None),
        "inference_mark_lte": asset_filter_kwargs.pop("inference_mark_lte", None),
        "metadata_where": asset_filter_kwargs.pop("metadata_where", None),
    }

    if asset_filter_kwargs:
        raise NameError(f"Unknown asset filter arguments: {list(asset_filter_kwargs.keys())}")

    if asset_where_params.get("label_category_search"):
        validate_category_search_query(asset_where_params["label_category_search"])  # type: ignore

    if asset_ids is not None and len(asset_ids) > 0:
        asset_where_params["asset_id_in"] = asset_ids

    where = AssetWhere(**asset_where_params)

    options = QueryOptions(disable_tqdm=disable_tqdm)
    post_call_function, fields = get_download_assets_function(
        auth, download_media, fields, project_id, local_media_dir
    )
    assets = list(AssetQuery(auth.client)(where, fields, options, post_call_function))
    _check_content_presence(assets)
    attach_name_to_assets_labels_author(assets, export_type)
    return assets


def _check_content_presence(assets: List[Dict]):
    if any(a.get("content") in [None, ""] and a.get("jsonContent") in [None, ""] for a in assets):
        raise NotExportableAssetError(
            "The assets cannot be exported. This can happen if they are hosted in a cloud storage."
        )


def get_fields_to_fetch(export_type: ExportType):
    """Returns the fields to fetch depending on the export type."""
    if export_type == "latest":
        return LATEST_LABEL_FIELDS
    return DEFAULT_FIELDS
