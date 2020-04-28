import pandas as pd

from ...helpers import deprecate, format_result
from ..asset import assets
from ..project import get_project
from .queries import GQL_LABELS


def labels(client, asset_id: str = None, label_id: str = None, project_id: str = None, user_id: str = None, skip: int = 0, first: int = None):
    formatted_first = first if first else 100
    variables = {
        'assetID': asset_id,
        'labelID': label_id,
        'projectID': project_id,
        'userID': user_id,
        'skip': skip,
        'first': formatted_first
    }
    result = client.execute(GQL_LABELS, variables)
    return format_result('data', result)


@deprecate(
    """
        This function is deprecated. get_label used to fetch labels from an asset_id and a user_id. It is now achievable with labels.
        To fetch labels from an asset_id and a user_id, use:
            > playground.labels(asset_id=asset_id, user_id=user_id)
        """)
def get_label(client, asset_id: str, user_id: str):
    return None


@deprecate(
    """
        This function is deprecated. get_latest_labels_for_user used to fetch labels from a project_id and a user_id. It is now achievable with labels.
        To fetch labels from a project_id and a user_id, use:
            > playground.labels(project_id=project_id, user_id=user_id)
        """)
def get_latest_labels_for_user(client, project_id: str, user_id: str):
    return None


@deprecate(
    """
        This function is deprecated. get_latest_labels used to fetch labels from a project_id. It is now achievable with labels.
        To fetch labels from a project_id, use:
            > playground.labels(project_id=project_id)
        """)
def get_latest_labels(client, project_id: str, skip: int, first: int):
    return None


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
    _assets = assets(client, project_id=project_id)
    labels = [dict(label, **dict((f'asset__{key}', asset[key]) for key in asset))
              for asset in _assets for label in asset['labels']]
    labels_df = pd.DataFrame(labels)
    labels_df['y'] = labels_df['jsonResponse'].apply(
        lambda json_response: parse_json_response(json_response, interface_category))
    return labels_df
