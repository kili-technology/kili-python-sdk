"""
Api key queries
"""

from typing import Optional

from typeguard import typechecked

from ...helpers import Compatible, format_result, fragment_builder
from .queries import gql_api_keys, GQL_API_KEYS_COUNT
from ...types import ApiKey as ApiKeyType


class QueriesApiKey:
    """
    Set of ApiKey queries
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
    @Compatible(['v2'])
    @typechecked
    def api_keys(self, api_key_id: Optional[str] = None, user_id: Optional[str] = None,
                 api_key: Optional[str] = None, skip: int = 0,
                 fields: list = ['id', 'name', 'createdAt', 'revoked'],
                 first: Optional[int] = 100):
        # pylint: disable=line-too-long
        """
        Get an array of api keys respecting a set of constraints

        Parameters
        ----------
        - api_key_id : str, optional (default = None)
            The unique id of the api key to retrieve.
        - user_id : str
            Identifier of the user (you can only query your own api keys).
        - api_key : str
            Value of the api key (you can only query your own api keys).
        - skip : int, optional (default = None)
            Number of assets to skip (they are ordered by their date of creation, first to last).
        - fields : list of string, optional (default = ['id', 'name', 'createdAt', 'revoked'])
            All the fields to request among the possible fields for the assets.
            See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#apikey) for all possible fields.
        - first : int, optional (default = None)
            Maximum number of assets to return. Can only be between 0 and 100.

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.

        Examples
        -------
        >>> kili.api_keys(user_id=user_id)
        >>> kili.api_keys(api_key=api_key)
        """
        variables = {
            'where': {
                'user': {
                    'id': user_id,
                    'apiKey': api_key
                },
                'id': api_key_id,
            },
            'skip': skip,
            'first': first,
        }
        _gql_issues = gql_api_keys(fragment_builder(fields, ApiKeyType))
        result = self.auth.client.execute(_gql_issues, variables)
        return format_result('data', result)

    @Compatible(['v2'])
    @typechecked
    def count_api_keys(self, api_key_id: Optional[str] = None, user_id: Optional[str] = None,
                       api_key: Optional[str] = None):
        """
        Count and return the number of api keys with the given constraints

        Parameters
        ----------
        - api_key_id : str, optional (default = None)
            The unique id of the api key to retrieve.
        - user_id : str
            Identifier of the user (you can only query your own api keys).
        - api_key : str
            Value of the api key (you can only query your own api keys).

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.

        Examples
        -------
        >>> kili.count_api_keys(user_id=user_id)
        3
        >>> kili.count_api_keys(api_key=api_key)
        1
        """
        variables = {
            'where': {
                'user': {
                    'id': user_id,
                    'apiKey': api_key
                },
                'id': api_key_id,
            },
        }
        result = self.auth.client.execute(GQL_API_KEYS_COUNT, variables)
        count = format_result('data', result)
        return count
