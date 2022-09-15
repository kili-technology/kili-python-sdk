"""
Set of common functions used by different export formats
"""
from typing import List, Optional

from kili.orm import AnnotationFormat

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


def attach_name_to_assets_labels_author(assets, export_type):
    """
    Adds `name` field for author, by concatenating his/her first and last name
    """
    for asset in assets:
        if export_type.lower() == AnnotationFormat.Latest.lower():
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
    kili,
    project_id: str,
    asset_ids: Optional[List[str]],
    export_type,
    label_type_in=None,
    disable_tqdm: bool = False,
):
    """
    Fetches assets where ID are in asset_ids if the list has more than one element,
    else all the assets of the project

    Parameters
    ----------
    - project_id: project id
    - assets_ids: list of asset IDs
    - export_type: type of export (latest label or all labels)
    - label_type_in: types of label to fetch (default, reviewed, ...)
    """
    fields = get_fields_to_fetch(export_type)
    assets = None
    if asset_ids is not None and len(asset_ids) > 0:
        assets = kili.assets(
            asset_id_in=asset_ids,
            project_id=project_id,
            fields=fields,
            label_type_in=label_type_in,
            disable_tqdm=disable_tqdm,
        )
    else:
        assets = kili.assets(
            project_id=project_id,
            fields=fields,
            label_type_in=label_type_in,
            disable_tqdm=disable_tqdm,
        )
    attach_name_to_assets_labels_author(assets, export_type)
    return assets


def get_fields_to_fetch(export_type):
    """
    Returns the fields to fetch depending on the export type
    """
    if export_type.lower() == AnnotationFormat.Latest.lower():
        return LATEST_LABEL_FIELDS
    return DEFAULT_FIELDS
