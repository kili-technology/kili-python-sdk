import pandas as pd
from typing import List
import warnings
from ...helpers import deprecate, format_result, fragment_builder
from ..asset import QueriesAsset
from ..project import QueriesProject
from .queries import gql_labels
from ...constants import NO_ACCESS_RIGHT
from ...types import Label


class QueriesLabel:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @deprecate(
        """
        This method is deprecated since: 30/04/2020.
        This method will be removed after: 30/05/2020.
        get_label used to fetch labels from an asset_id and a user_id. It is now achievable with labels.
        To fetch labels from an asset_id and a user_id, use:
            > playground.labels(asset_id=asset_id, user_id=user_id)
        """)
    def get_label(self, asset_id: str, user_id: str):
        labels = self.labels(asset_id=asset_id, user_id=user_id)
        assert len(labels) == 1, NO_ACCESS_RIGHT
        return labels[0]

    @deprecate(
        """
        This method is deprecated since: 30/04/2020.
        This method will be removed after: 30/05/2020.
        get_latest_labels_for_user used to fetch labels from a project_id and a user_id. It is now achievable with labels.
        To fetch labels from a project_id and a user_id, use:
            > playground.labels(project_id=project_id, user_id=user_id)
        """)
    def get_latest_labels_for_user(self, project_id: str, user_id: str):
        return self.labels(project_id=project_id, user_id=user_id)

    @deprecate(
        """
        This method is deprecated since: 30/04/2020.
        This method will be removed after: 30/05/2020.
        get_latest_labels used to fetch labels from a project_id. It is now achievable with labels.
        To fetch labels from a project_id, use:
            > playground.labels(project_id=project_id, first=first, skip=skip)
        """)
    def get_latest_labels(self, project_id: str, skip: int, first: int):
        return self.labels(project_id=project_id, first=first, skip=skip)

    @deprecate(
        """
        **New feature has been added : Query only the fields you want
        using the field argument, that accept a list of string organized like below.**
        The former default query with all fields is deprecated since 13/05/2020
        After 13/06/2020, the default queried fields will be :
        ['id', 'author.id','author.name', 'author.email', 'jsonResponse', 
        'labelType', 'secondsToLabel', 'skipped']
        To fetch more fields, for example the consensus fields, just add those :
        fields = ['id','honeypotMark','numberOfAnnotations','jsonResponse','labelType',
        'skipped','createdAt', 'author.email', 'author.name', 'author.organization.name', 
        'author.organization.zipCode']
        """)
    def labels(self,
               asset_id: str = None,
               asset_status_in: List[str] = None,
               asset_external_id_in: List[str] = None,
               author_in: List[str] = None,
               created_at: str = None,
               created_at_gte: str = None,
               created_at_lte: str = None,
               fields: list = ['author.email', 'author.id',
                               'id', 'jsonResponse', 'numberOfAnnotations'],
               first: int = None,
               honeypot_mark_gte: float = None,
               honeypot_mark_lte: float = None,
               label_id: str = None,
               project_id: str = None,
               skip: int = 0,
               skipped: bool = None,
               type_in: List[str] = None,
               user_id: str = None):
        """
        Get an array of labels from a project

        Parameters
        ----------
        - asset_id : str
            Identifier of the asset.
        - asset_status_in : list of str, optional (default = None)
            Returned labels should have a status that belongs to that list, if given.
            Possible choices : {'TODO', 'ONGOING', 'LABELED', 'REVIEWED'}
        - asset_external_id_in : list of str, optional (default = None)
            Returned labels should have an external id that belongs to that list, if given.
        - author_in : list of str, optional (default = None)
            Returned labels should have a label whose status belongs to that list, if given.
        - created_at : float, optional (default = None)
            Returned labels should have a label whose creation date is equal to this date.
        - created_at_gt : float, optional (default = None)
            Returned labels should have a label whose creation date is greater than this date.
        - created_at_lt : float, optional (default = None)
            Returned labels should have a label whose creation date is lower than this date.
        - fields : list of string, optional (default = ['author.email', 'author.id','author.name', 'id', 'jsonResponse', 'labelType', 'secondsToLabel', 'skipped'])
            All the fields to request among the possible fields for the labels, default for None are the non-calculated fields)
            Possible fields : see https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#label
        - first : int, optional (default = None)
            Maximum number of labels to return.  Can only be between 0 and 100.
        - honeypot_mark_gt : float, optional (default = None)
            Returned labels should have a label whose honeypot is greater than this number.
        - honeypot_mark_lt : float, optional (default = None)
            Returned labels should have a label whose honeypot is lower than this number.
        - label_id : str
            Identifier of the label.
        - project_id : str
            Identifier of the project.
        - skip : int, optional (default = None)
            Number of labels to skip (they are ordered by their date of creation, first to last).
        - skipped : bool, optional (default = None)
            Returned labels should have a label which is skipped
        - type_in : list of str, optional (default = None)
            Returned labels should have a label whose type belongs to that list, if given.
        - user_id : str
            Identifier of the user.


        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        formatted_first = first if first else 100
        variables = {
            'where': {
                'id': label_id,
                'asset': {
                    'id': asset_id,
                    'externalIdIn': asset_external_id_in,
                    'statusIn': asset_status_in,
                },
                'project': {
                    'id': project_id,
                },
                'user': {
                    'id': user_id,
                },
                'typeIn': type_in,
                'authorIn': author_in,
                'honeypotMarkGte': honeypot_mark_gte,
                'honeypotMarkLte': honeypot_mark_lte,
                'createdAt': created_at,
                'createdAtGte': created_at_gte,
                'createdAtLte': created_at_lte,
                'skipped': skipped,
            },
            'skip': skip,
            'first': formatted_first,
        }
        GQL_LABELS = gql_labels(fragment_builder(fields, Label))
        result = self.auth.client.execute(GQL_LABELS, variables)
        return format_result('data', result)

    def parse_json_response_for_single_classification(self, json_response):
        """
        Get the names of categories from a json_response, for a single class - classification task
        """
        categories = self.parse_json_response_for_multi_classification(
            json_response)
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

    def export_labels_as_df(self, project_id: str, fields: list = None):
        """
        Get the labels of a project as a pandas DataFrame

        Parameters
        ----------
        - project_id : str
        - fields : list of string, optional (default = None)
            All the fields to request among the possible fields for the labels, default for None are the non-calculated fields)
            - Possible fields : see https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#label
            - Default fields : `['id', 'author.id','author.name', 'author.email', 'jsonResponse', 'labelType', 'secondsToLabel', 'skipped']`

        Returns
        -------
        - labels_df : pandas DataFrame containing the labels.
        """
        projects = QueriesProject(self.auth).projects(project_id)
        assert len(projects) == 1, NO_ACCESS_RIGHT
        project = projects[0]
        if 'interfaceCategory' not in project:
            return pd.DataFrame()

        interface_category = project['interfaceCategory']
        assets = QueriesAsset(self.auth).assets(
            project_id=project_id, fields=fields)
        labels = [dict(label, **dict((f'asset__{key}', asset[key]) for key in asset))
                  for asset in assets for label in asset['labels']]
        labels_df = pd.DataFrame(labels)
        labels_df['y'] = labels_df['jsonResponse'].apply(
            lambda json_response: self.parse_json_response(json_response, interface_category))
        return labels_df
