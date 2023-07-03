"""Helpers for the asset mutations."""
from typing import Dict, List, Optional, Union

from kili.core.helpers import convert_to_list_of_none, format_metadata, is_none_or_empty
from kili.entrypoints.mutations.helpers import check_asset_identifier_arguments
from kili.services.helpers import infer_ids_from_external_ids
from kili.utils.assets import PageResolution


def process_update_properties_in_assets_parameters(properties) -> Dict:
    """Process arguments of the update_properties_in_assets method
    and return the properties for the paginated loop.

    properties should have the following keys:
        - asset_ids: list of asset ids.
        - json_metadatas: list of json metadatas, can be none.
        - to_be_labeled_by_array: list of users, must be iterable.
        - page_resolutions_array: list of page resolutions, must be iterable.
    """
    formatted_json_metadatas = None
    if properties["json_metadatas"] is None:
        formatted_json_metadatas = None
    else:
        if isinstance(properties["json_metadatas"], list):
            formatted_json_metadatas = list(map(format_metadata, properties["json_metadatas"]))
        else:
            raise TypeError(
                "json_metadatas",
                "Should be either a None or a list of None, string, list or dict",
            )
    properties["json_metadatas"] = formatted_json_metadatas
    assert properties["asset_ids"]
    nb_assets_to_modify = len(properties["asset_ids"])
    properties = {
        k: convert_to_list_of_none(v, length=nb_assets_to_modify) for k, v in properties.items()
    }
    properties["should_reset_to_be_labeled_by_array"] = list(
        map(is_none_or_empty, properties["to_be_labeled_by_array"])
    )

    properties["page_resolutions_array"] = _ensure_page_resolution_dicts(
        properties["page_resolutions_array"]
    )

    return properties


def _ensure_page_resolution_dicts(
    page_resolutions_array: Union[List[List[PageResolution]], List[List[Dict]]]
):
    page_resolutions_array_batch = []
    for page_resolution_array in page_resolutions_array:
        output_page_resolution_array = []
        for page_resolution in page_resolution_array:
            output_page_resolution_array.append(
                page_resolution.as_dict()
                if isinstance(page_resolution, PageResolution)
                else page_resolution
            )
        page_resolutions_array_batch.append(output_page_resolution_array)
    return page_resolutions_array_batch


def get_asset_ids_or_throw_error(
    kili,
    asset_ids: Optional[List[str]],
    external_ids: Optional[List[str]],
    project_id: Optional[str],
) -> List[str]:
    """Check if external id to internal id conversion is valid and needed."""
    check_asset_identifier_arguments(project_id, asset_ids, external_ids)

    if asset_ids is None:
        id_map = infer_ids_from_external_ids(
            kili=kili, asset_external_ids=external_ids, project_id=project_id  # type: ignore
        )
        asset_ids = [id_map[id] for id in external_ids]  # type: ignore

    return asset_ids
