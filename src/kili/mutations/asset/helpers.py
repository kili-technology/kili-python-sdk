"""
Helpers for the asset mutations
"""
from typing import Dict, List, Optional

from kili.services.helpers import infer_ids_from_external_ids

from ...helpers import convert_to_list_of_none, format_metadata, is_none_or_empty


def process_update_properties_in_assets_parameters(properties) -> Dict:
    """
    Process arguments of the update_properties_in_assets method
    and return the properties for the paginated loop
    """
    formatted_json_metadatas = None
    if properties["json_metadatas"] is None:
        formatted_json_metadatas = None
    else:
        if isinstance(properties["json_metadatas"], list):
            formatted_json_metadatas = list(map(format_metadata, properties["json_metadatas"]))
        else:
            raise Exception(
                "json_metadatas",
                "Should be either a None or a list of None, string, list or dict",
            )
    properties["json_metadatas"] = formatted_json_metadatas
    nb_assets_to_modify = len(properties["asset_ids"])
    properties = {
        k: convert_to_list_of_none(v, length=nb_assets_to_modify) for k, v in properties.items()
    }
    properties["should_reset_to_be_labeled_by_array"] = list(
        map(is_none_or_empty, properties["to_be_labeled_by_array"])
    )
    return properties


def get_asset_ids_or_throw_error(
    kili,
    asset_ids: Optional[List[str]] = None,
    external_ids: Optional[List[str]] = None,
    project_id: Optional[str] = None,
) -> List[str]:
    """
    Check if external id to internal id is valid and needed.
    """
    if asset_ids is None and external_ids is None:
        raise ValueError("Please provide either `asset_ids` or `external_ids`.")

    if external_ids is not None and asset_ids is None:
        if project_id is None:
            raise ValueError("Please provide `project_id` if `external_ids` is given.")
        id_map = infer_ids_from_external_ids(
            kili=kili, asset_external_ids=external_ids, project_id=project_id
        )
        asset_ids = [id_map[id] for id in external_ids]

    return asset_ids  # type: ignore
