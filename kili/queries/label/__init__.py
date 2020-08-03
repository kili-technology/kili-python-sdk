import pandas as pd
from typing import List
import warnings
from ...helpers import deprecate, format_result, fragment_builder
from ..asset import QueriesAsset
from ..project import QueriesProject
from .queries import gql_labels, GQL_LABELS_COUNT
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

    def labels(self,
               asset_id: str = None,
               asset_status_in: List[str] = None,
               asset_external_id_in: List[str] = None,
               author_in: List[str] = None,
               created_at: str = None,
               created_at_gte: str = None,
               created_at_lte: str = None,
               fields: list = ['author.email', 'author.id', 'author.name', 'id',
                               'jsonResponse', 'labelType', 'secondsToLabel', 'skipped'],
               first: int = None,
               honeypot_mark_gte: float = None,
               honeypot_mark_lte: float = None,
               json_response_contains: List[str] = None,
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
        - created_at : string, optional (default = None)
            Returned labels should have a label whose creation date is equal to this date.
            Formatted string should have format : "YYYY-MM-DD"
        - created_at_gt : string, optional (default = None)
            Returned labels should have a label whose creation date is greater than this date.
            Formatted string should have format : "YYYY-MM-DD"
        - created_at_lt : string, optional (default = None)
            Returned labels should have a label whose creation date is lower than this date.
            Formatted string should have format : "YYYY-MM-DD"
        - fields : list of string, optional (default = ['author.email', 'author.id','author.name', 'id', 'jsonResponse', 'labelType', 'secondsToLabel', 'skipped'])
            All the fields to request among the possible fields for the labels, default for None are the non-calculated fields)
            Possible fields : see https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#label
        - first : int, optional (default = None)
            Maximum number of labels to return.  Can only be between 0 and 100.
        - honeypot_mark_gt : float, optional (default = None)
            Returned labels should have a label whose honeypot is greater than this number.
        - honeypot_mark_lt : float, optional (default = None)
            Returned labels should have a label whose honeypot is lower than this number.
        - json_response_contains : list of str, optional (default = None)
            Returned labels should have a substring of the jsonResponse that belongs to that list, if given.
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
                'createdAt': created_at,
                'createdAtGte': created_at_gte,
                'createdAtLte': created_at_lte,
                'authorIn': author_in,
                'honeypotMarkGte': honeypot_mark_gte,
                'honeypotMarkLte': honeypot_mark_lte,
                'jsonResponseContains': json_response_contains,
                'skipped': skipped,
                'typeIn': type_in,
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

    def export_labels_as_df(self,
                            project_id: str,
                            fields: list = ['author.email', 'author.id', 'author.name', 'createdAt', 'id', 'labelType', 'skipped']):
        """
        Get the labels of a project as a pandas DataFrame

        Parameters
        ----------
        - project_id : str
        - fields : list of string, optional (default = [ 'author.email', 'author.id','author.name', 'id', 'jsonResponse', 'labelType', 'secondsToLabel', 'skipped'])
            All the fields to request among the possible fields for the labels, default are the non-calculated fields)
            - Possible fields : see https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#label
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

    def count_labels(self,
                     asset_id: str = None,
                     asset_status_in: List[str] = None,
                     asset_external_id_in: List[str] = None,
                     author_in: List[str] = None,
                     created_at: str = None,
                     created_at_gte: str = None,
                     created_at_lte: str = None,
                     fields: list = ['author.email', 'author.id', 'author.name', 'id',
                                     'jsonResponse', 'labelType', 'secondsToLabel', 'skipped'],
                     honeypot_mark_gte: float = None,
                     honeypot_mark_lte: float = None,
                     json_response_contains: List[str] = None,
                     label_id: str = None,
                     project_id: str = None,
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
        - created_at : string, optional (default = None)
            Returned labels should have a label whose creation date is equal to this date.
            Formatted string should have format : "YYYY-MM-DD"
        - created_at_gt : string, optional (default = None)
            Returned labels should have a label whose creation date is greater than this date.
            Formatted string should have format : "YYYY-MM-DD"
        - created_at_lt : string, optional (default = None)
            Returned labels should have a label whose creation date is lower than this date.
            Formatted string should have format : "YYYY-MM-DD"
        - fields : list of string, optional (default = ['author.email', 'author.id','author.name', 'id', 'jsonResponse', 'labelType', 'secondsToLabel', 'skipped'])
            All the fields to request among the possible fields for the labels, default for None are the non-calculated fields)
            Possible fields : see https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#label
        - honeypot_mark_gt : float, optional (default = None)
            Returned labels should have a label whose honeypot is greater than this number.
        - honeypot_mark_lt : float, optional (default = None)
            Returned labels should have a label whose honeypot is lower than this number.
        - json_response_contains : list of str, optional (default = None)
            Returned labels should have a substring of the jsonResponse that belongs to that list, if given.
        - label_id : str
            Identifier of the label.
        - project_id : str
            Identifier of the project.
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
                'createdAt': created_at,
                'createdAtGte': created_at_gte,
                'createdAtLte': created_at_lte,
                'authorIn': author_in,
                'honeypotMarkGte': honeypot_mark_gte,
                'honeypotMarkLte': honeypot_mark_lte,
                'jsonResponseContains': json_response_contains,
                'skipped': skipped,
                'typeIn': type_in,
            }
        }
        result = self.auth.client.execute(GQL_LABELS_COUNT, variables)
        count = format_result('data', result)
        return count
