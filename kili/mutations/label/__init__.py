from json import dumps
from typing import List

from ...helpers import format_result
from .queries import (GQL_APPEND_TO_LABELS, GQL_CREATE_HONEYPOT,
                      GQL_CREATE_PREDICTIONS, GQL_UPDATE_LABEL,
                      GQL_UPDATE_PROPERTIES_IN_LABEL)


def create_predictions(client, project_id: str, external_id_array: List[str], model_name_array: List[str], json_response_array: List[dict]):
    assert len(external_id_array) == len(
        json_response_array), "IDs list and predictions list should have the same length"
    assert len(external_id_array) == len(
        model_name_array), "IDs list and model names list should have the same length"
    variables = {
        'projectID': project_id,
        'externalIDArray': external_id_array,
        'modelNameArray': model_name_array,
        'jsonResponseArray': [dumps(elem) for elem in json_response_array]
    }
    result = client.execute(GQL_CREATE_PREDICTIONS, variables)
    return format_result('data', result)


def append_to_labels(client, author_id: str, json_response: dict, label_asset_id: str, label_type: str, seconds_to_label: int, skipped: bool = False):
    variables = {
        'authorID': author_id,
        'jsonResponse': dumps(json_response),
        'labelAssetID': label_asset_id,
        'labelType': label_type,
        'secondsToLabel': seconds_to_label,
        'skipped': skipped
    }
    result = client.execute(GQL_APPEND_TO_LABELS, variables)
    return format_result('data', result)


def update_label(client, label_id: str, label_asset_id: str, review_asset_id: str, author_id: str, label_type: str, json_response: dict, seconds_to_label: int):
    variables = {
        'labelID': label_id,
        'labelAssetID': label_asset_id,
        'reviewAssetID': review_asset_id,
        'authorID': author_id,
        'labelType': label_type,
        'jsonResponse': dumps(json_response),
        'secondsToLabel': seconds_to_label
    }
    result = client.execute(GQL_UPDATE_LABEL, variables)
    return format_result('data', result)


def update_properties_in_label(client, label_id: str, seconds_to_label: int = None, model_name: str = None, json_response: dict = None):
    formatted_json_response = None if json_response is None else dumps(
        json_response)
    variables = {
        'labelID': label_id,
        'secondsToLabel': seconds_to_label,
        'modelName': model_name,
        'jsonResponse': formatted_json_response
    }
    result = client.execute(GQL_UPDATE_PROPERTIES_IN_LABEL, variables)
    return format_result('data', result)


def create_honeypot(client, asset_id: str, json_response: dict):
    variables = {
        'assetID': asset_id,
        'jsonResponse': dumps(json_response)
    }
    result = client.execute(GQL_CREATE_HONEYPOT, variables)
    return format_result('data', result)
