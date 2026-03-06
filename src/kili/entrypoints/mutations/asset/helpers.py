"""Helpers for the asset mutations."""

from collections.abc import Callable
from typing import Optional, Union

from kili.core.helpers import convert_to_list_of_none, format_metadata, is_none_or_empty
from kili.utils.assets import PageResolution


# pylint: disable=too-many-locals
def process_update_properties_in_assets_parameters(
    asset_ids: list[str],
    *,
    external_ids: Optional[list[str]] = None,
    priorities: Optional[list[int]] = None,
    json_metadatas: Optional[list[Union[dict, str]]] = None,
    consensus_marks: Optional[list[float]] = None,
    honeypot_marks: Optional[list[float]] = None,
    to_be_labeled_by_array: Optional[list[list[str]]] = None,
    contents: Optional[list[str]] = None,
    json_contents: Optional[list[str]] = None,
    is_used_for_consensus_array: Optional[list[bool]] = None,
    is_honeypot_array: Optional[list[bool]] = None,
    resolution_array: Optional[list[dict]] = None,
    page_resolutions_array: Optional[Union[list[list[dict]], list[list[PageResolution]]]] = None,
) -> dict:
    """Process arguments of the update_properties_in_assets method.

    Return the properties for the paginating loop.
    """
    assert asset_ids
    nb_assets_to_modify = len(asset_ids)

    input_handlers: dict[str, Callable[[list], list]] = {
        "jsonMetadata": _handle_json_metadata,
        "shouldResetToBeLabeledBy": _handle_should_reset_to_be_labeled_by,
        "pageResolutions": _handle_page_resolutions_array,
    }

    argument_to_gql_mapping = {
        "assetId": asset_ids,
        "externalId": external_ids,
        "priority": priorities,
        "jsonMetadata": json_metadatas,
        "consensusMark": consensus_marks,
        "honeypotMark": honeypot_marks,
        "toBeLabeledBy": to_be_labeled_by_array,
        "shouldResetToBeLabeledBy": to_be_labeled_by_array,
        "content": contents,
        "jsonContent": json_contents,
        "isUsedForConsensus": is_used_for_consensus_array,
        "isHoneypot": is_honeypot_array,
        "pageResolutions": page_resolutions_array,
        "resolution": resolution_array,
    }

    return {
        k: input_handlers.get(k, lambda x: x)(convert_to_list_of_none(v, nb_assets_to_modify))
        for k, v in argument_to_gql_mapping.items()
        if v is not None
    }


# pylint: enable=too-many-locals


def _handle_page_resolutions_array(
    page_resolutions_array: Union[list[list[PageResolution]], list[list[dict]]],
) -> list[list[dict]]:
    page_resolutions_array_batch = []
    for page_resolution_array in page_resolutions_array:
        if page_resolution_array is None:
            page_resolutions_array_batch.append(None)
            continue

        output_page_resolution_array = []
        for page_resolution in page_resolution_array:
            output_page_resolution_array.append(
                page_resolution.as_dict()
                if isinstance(page_resolution, PageResolution)
                else page_resolution
            )
        page_resolutions_array_batch.append(output_page_resolution_array)
    return page_resolutions_array_batch


def _handle_should_reset_to_be_labeled_by(to_be_labeled_by_array):
    return list(map(is_none_or_empty, to_be_labeled_by_array))


def _handle_json_metadata(json_metadatas) -> list:
    return list(map(format_metadata, json_metadatas))
