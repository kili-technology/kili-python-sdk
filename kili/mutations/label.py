from json import dumps
from typing import List

from ..helpers import format_result, json_escape


def create_prediction(client, asset_id: str, json_response: str):
    print('create_prediction is deprecated. Please use create_predictions instead. For an example, see: https://github.com/kili-technology/kili-playground/blob/master/recipes/import_predictions.py')


def create_predictions(client, project_id: str, external_id_array: List[str], model_name_array: List[str], json_response_array: List[dict]):
    assert len(external_id_array) == len(
        json_response_array), "IDs list and predictions list should have the same length"
    assert len(external_id_array) == len(
        model_name_array), "IDs list and model names list should have the same length"
    result = client.execute('''
    mutation {
      createPredictions(
        projectID: "%s",
        externalIDArray: %s,
        modelNameArray: %s,
        jsonResponseArray: %s) {
          id
      }
    }
    ''' % (project_id, dumps(external_id_array), dumps(model_name_array), dumps([dumps(elem) for elem in json_response_array])))
    return format_result('createPredictions', result)


def append_to_labels(client, author_id: str, json_response: dict, label_asset_id: str, label_type: str, seconds_to_label: int, skipped: bool = False):
    result = client.execute('''
    mutation {
      appendToLabels(
        authorID: "%s",
        jsonResponse: "%s",
        labelAssetID: "%s",
        labelType: %s,
        secondsToLabel: %d,
        skipped: %s) {
          id
      }
    }
    ''' % (author_id, json_escape(json_response), label_asset_id, label_type, seconds_to_label, str(skipped).lower()))
    return format_result('appendToLabels', result)


def update_label(client, label_id: str, label_asset_id: str, review_asset_id: str, author_id: str, label_type: str, json_response: dict, seconds_to_label: int):
    result = client.execute('''
    mutation {
      updateLabel(
        labelID: "%s",
        labelAssetID: "%s",
        reviewAssetID: "%s",
        authorID: "%s",
        labelType: %s,
        jsonResponse: "%s",
        secondsToLabel: %d) {
          id
      }
    }
    ''' % (label_id, label_asset_id, review_asset_id, author_id, label_type, json_escape(json_response), seconds_to_label))
    return format_result('updateLabel', result)


def update_properties_in_label(client, label_id: str, seconds_to_label: int = None, model_name: str = None, json_response: dict = None):
    formatted_seconds_to_label = 'null' if seconds_to_label is None else f'{seconds_to_label}'
    formatted_json_response = 'null' if json_response is None else f'{json_escape(json_response)}'
    formatted_model_name = 'null' if model_name is None else f'{model_name}'

    result = client.execute('''
        mutation {
          updatePropertiesInLabel(
            where: {id: "%s"},
            data: {
              secondsToLabel: %s
              modelName: "%s"
              jsonResponse: "%s"
            }
          ) {
            id
          }
        }
        ''' % (label_id, formatted_seconds_to_label, formatted_model_name, formatted_json_response))
    return format_result('updatePropertiesInLabel', result)
