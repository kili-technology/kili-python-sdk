import pandas as pd

from ...helpers import format_result
from ..asset import get_assets
from ..project import get_project
from .queries import (GQL_GET_LABEL, GQL_GET_LATEST_LABELS,
                      GQL_GET_LATEST_LABELS_FOR_USER)


class QueriesLabel:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    def get_label(self, asset_id: str, user_id: str):
        """
        Get labels corresponding to a given asset and user

        Parameters
        ----------
        - asset_id : str
        - user_id : str

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        return get_label(self.auth.client, asset_id, user_id)


    def get_latest_labels_for_user(self, project_id: str, user_id: str):
        """
        Get latest labels corresponding to a given user and project

        Parameters
        ----------
        - project_id : str
        - user_id : str

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        variables = {'projectID': project_id, 'userID': user_id}
        result = self.auth.client.execute(GQL_GET_LATEST_LABELS_FOR_USER, variables)
        return format_result('data', result)


    def get_latest_labels(self, project_id: str, skip: int, first: int):
        """
        Get latest labels corresponding to a given project

        Parameters
        ----------
        - project_id : str
        - skip : int
            Number of labels to skip when returning them.
        - first : int
            Maximum number of labels returned.

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        variables = {'projectID': project_id, 'skip': skip, 'first': first}
        result = self.auth.client.execute(GQL_GET_LATEST_LABELS, variables)
        return format_result('data', result)


    def parse_json_response_for_single_classification(self, json_response):
        """
        Get the names of categories from a json_response, for a single class - classification task
        """
        categories = self.parse_json_response_for_multi_classification(json_response)
        if len(categories) == 0:
            return []

        return categories[0]


    def parse_json_response_for_multi_classification(self, json_response):
        """
        Get the names of categories from a json_response, for a multi class - classification task
        """
        formatted_json_response = eval(json_response)
        if 'categories' not in formatted_json_response:
            return []
        categories = formatted_json_response['categories']
        return list(map(lambda category: category['name'], categories))


    def parse_json_response(self, json_response, interface_category):
        if interface_category == 'SINGLECLASS_TEXT_CLASSIFICATION':
            return self.parse_json_response_for_single_classification(json_response)
        if interface_category == 'MULTICLASS_TEXT_CLASSIFICATION':
            return self.parse_json_response_for_multi_classification(json_response)

        return json_response


    def export_labels_as_df(self, project_id: str):
        """
        Get the labels of a project as a pandas DataFrame

        Parameters
        ----------
        - project_id : str

        Returns
        -------
        - labels_df : pandas DataFrame containing the labels.
        """
        project = get_project(self.auth.client, project_id)
        if 'interfaceCategory' not in project:
            return pd.DataFrame()

        interface_category = project['interfaceCategory']
        assets = get_assets(self.auth.client, project_id=project_id)
        labels = [dict(label, **dict((f'asset__{key}', asset[key]) for key in asset))
                for asset in assets for label in asset['labels']]
        labels_df = pd.DataFrame(labels)
        labels_df['y'] = labels_df['jsonResponse'].apply(
            lambda json_response: self.parse_json_response(json_response, interface_category))
        return labels_df


def get_label(client, asset_id: str, user_id: str):
    variables = {'assetID': asset_id, 'userID': user_id}
    result = client.execute(GQL_GET_LABEL, variables)
    return format_result('data', result)