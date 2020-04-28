from json import dumps
from typing import List

from ...helpers import content_escape, encode_image, format_result, is_url, deprecate
from ...queries.project import get_project
from .queries import (GQL_APPEND_MANY_TO_DATASET,
                      GQL_DELETE_MANY_FROM_DATASET,
                      GQL_UPDATE_PROPERTIES_IN_ASSET)


@deprecate(
    """
        This function is deprecated. delete_assets_by_external_id used to delete some assets matchin on external ID. It is now achievable with get_assets and delete_many_from_dataset.
        To fetch ann asset from its ID, use:
            > assets = playground.assets(project_id=project_id, external_id_contains=[external_id])
            > playground.delete_many_from_dataset(asset_ids=[a['id] for a in assets])
        """)
def delete_assets_by_external_id(client, project_id: str, external_id: str):
    return None


def append_many_to_dataset(client, project_id: str, content_array: List[str], external_id_array: List[str],
                           is_honeypot_array: List[bool] = None, status_array: List[str] = None, json_metadata_array: List[dict] = None):
    is_honeypot_array = [
        False] * len(content_array) if not is_honeypot_array else is_honeypot_array
    status_array = ['TODO'] * \
        len(content_array) if not status_array else status_array
    json_metadata_array = [
        {}] * len(content_array) if not json_metadata_array else json_metadata_array
    formatted_json_metadata_array = [
        dumps(elem) for elem in json_metadata_array]
    input_type = get_project(client, project_id)['inputType']
    if input_type == 'IMAGE':
        content_array = [content if is_url(content) else encode_image(
            content) for content in content_array]
    variables = {
        'projectID': project_id,
        'contentArray': content_array,
        'externalIDArray': external_id_array,
        'isHoneypotArray': is_honeypot_array,
        'statusArray': status_array,
        'jsonMetadataArray': formatted_json_metadata_array}
    result = client.execute(GQL_APPEND_MANY_TO_DATASET, variables)
    return format_result('data', result)


def update_properties_in_asset(client, asset_id: str, external_id: str = None,
                               priority: int = None, json_metadata: dict = None, consensus_mark: float = None,
                               honeypot_mark: float = None, to_be_labeled_by: List[str] = None, content: str = None,
                               status: str = None, is_used_for_consensus: bool = None, is_honeypot: bool = None):
    formatted_json_metadata = None
    if json_metadata is None:
        formatted_json_metadata = None
    elif isinstance(json_metadata, str):
        formatted_json_metadata = json_metadata
    elif isinstance(json_metadata, dict) or isinstance(json_metadata, list):
        formatted_json_metadata = dumps(json_metadata)
    else:
        raise Exception('json_metadata',
                        'Should be either a dict, a list or a string url')
    variables = {
        'assetID': asset_id,
        'externalID': external_id,
        'priority': priority,
        'jsonMetadata': formatted_json_metadata,
        'consensusMark': consensus_mark,
        'honeypotMark': honeypot_mark,
        'toBeLabeledBy': to_be_labeled_by,
        'content': content,
        'status': status,
        'isUsedForConsensus': is_used_for_consensus,
        'isHoneypot': is_honeypot,
    }
    result = client.execute(GQL_UPDATE_PROPERTIES_IN_ASSET, variables)
    return format_result('data', result)


def delete_many_from_dataset(client, asset_ids: List[str]):
    variables = {'assetIDs': asset_ids}
    result = client.execute(GQL_DELETE_MANY_FROM_DATASET, variables)
    return format_result('data', result)
