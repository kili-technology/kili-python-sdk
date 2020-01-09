import pandas as pd

from ..helper import format_result
from .asset import get_assets
from .project import get_project


def get_label(client, asset_id: str, user_id: str):
    result = client.execute('''
    query {
      getLabel(assetID: "%s", userID: "%s") {
        id
        jsonResponse
        numberOfAnnotations
      }
    }
    ''' % (asset_id, user_id))
    return format_result('getLabel', result)


def get_latest_labels_for_user(client, project_id: str, user_id: str):
    result = client.execute('''
    query {
      getLatestLabelsForUser(projectID: "%s", userID: "%s") {
        id
        jsonResponse
      }
    }
    ''' % (project_id, user_id))
    return format_result('getLatestLabelsForUser', result)


def get_latest_labels(client, project_id: str, skip: int, first: int):
    result = client.execute('''
    query {
      getLatestLabels(projectID: "%s", skip: %d, first: %d) {
        id
        jsonResponse
      }
    }
    ''' % (project_id, skip, first))
    return format_result('getLatestLabels', result)


def parse_json_response_for_single_classification(json_response):
    categories = parse_json_response_for_multi_classification(json_response)
    if len(categories) == 0:
        return []

    return categories[0]


def parse_json_response_for_multi_classification(json_response):
    formatted_json_response = eval(json_response)
    if 'categories' not in formatted_json_response:
        return []
    categories = formatted_json_response['categories']
    return list(map(lambda category: category['name'], categories))


def parse_json_response(json_response, interface_category):
    if interface_category == 'SINGLECLASS_TEXT_CLASSIFICATION':
        return parse_json_response_for_single_classification(json_response)
    if interface_category == 'MULTICLASS_TEXT_CLASSIFICATION':
        return parse_json_response_for_multi_classification(json_response)

    return json_response


def export_labels_as_df(client, project_id: str):
    project = get_project(client, project_id)
    if 'interfaceCategory' not in project:
        return pd.DataFrame()

    interface_category = project['interfaceCategory']
    assets = get_assets(client, project_id=project_id)
    labels = [dict(label, **dict((f'asset__{key}', asset[key]) for key in asset))
              for asset in assets for label in asset['labels']]
    labels_df = pd.DataFrame(labels)
    labels_df['y'] = labels_df['jsonResponse'].apply(
        lambda json_response: parse_json_response(json_response, interface_category))
    return labels_df
