"""
Project queries
"""

from typing import Optional
from typeguard import typechecked

from ...helpers import Compatible, deprecate, format_result, fragment_builder
from .queries import gql_datasets, GQL_DATASETS_COUNT
from ...types import Dataset


class QueriesDataset:
    """
    Set of Dataset queries
    """
    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    # pylint: disable=dangerous-default-value
    @Compatible(['v1', 'v2'])
    @typechecked
    def datasets(self,
                 dataset_id: Optional[str] = None,
                 skip: int = 0,
                 fields: list = [
                     'id',
                     'createdAt',
                     'updatedAt',
                     'assets.id',
                     'name',
                     'numberOfAssets',
                     'projectId',
                     'type',
                     'users.email',
                 ],
                 first: int = 100):
        # pylint: disable=line-too-long
        """
        Get datasets given a set of criteria

        Parameters
        ----------
        - dataset_id : str, optional (default = None)
            Select a specific project through its project_id.
        - skip : int, optional (default = 0)
            Number of datasets to skip (they are ordered by their creation).
        - fields : list of string, optional (default = ['id',
            ])
            All the fields to request among the possible fields for the datasets.
            See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#project) for all possible fields.
        - first : int , optional (default = 100)
            Maximum number of datasets to return. Can only be between 0 and 100.

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.

        Examples
        -------
        >>> # List all my datasets
        >>> kili.datasets()
        """
        _gql_datasets = gql_datasets(fragment_builder(fields, Dataset))
        variables = {
            'where': {
                'id': dataset_id,
            },
            'skip': skip,
            'first': first
        }
        result = self.auth.client.execute(_gql_datasets, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    @typechecked
    def count_datasets(
            self,
            dataset_id: Optional[str] = None):
        """
        Counts the number of datasets with a search_query

        Parameters
        ----------
        - dataset_id : str, optional (default = None)
            Select a specific dataset through its dataset_id

        Returns
        -------
        - a positive integer corresponding to the number of results of the query
            if it was successful, or an error message else.
        """
        variables = {
            'where': {
                'id': dataset_id,
            }
        }
        result = self.auth.client.execute(GQL_DATASETS_COUNT, variables)
        count = format_result('data', result)
        return count
