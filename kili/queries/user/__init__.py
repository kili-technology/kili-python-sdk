"""
User queries
"""

from typing import Generator, List, Optional, Union
import warnings

from typeguard import typechecked


from ...helpers import Compatible, format_result, fragment_builder
from .queries import gql_users, GQL_USERS_COUNT
from ...types import User
from ...utils import row_generator_from_paginated_calls


class QueriesUser:
    """
    Set of User queries
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
    def users(self,
              api_key: Optional[str] = None,
              email: Optional[str] = None,
              organization_id: Optional[str] = None,
              fields: list = ['email', 'id', 'firstname', 'lastname'],
              first: int = 100,
              skip: int = 0,
              disable_tqdm: bool = False,
              as_generator: bool = False) -> Union[List[dict], Generator[dict, None, None]]:
        # pylint: disable=line-too-long
        """
        Gets a generator or a list of users given a set of criteria

        Parameters
        ----------
        - api_key : str, optional (default = None) Query an user by its API KEY
        - email : str, optional (default = None)
        - organization_id : str, optional (default = None)
        - fields : list of string, optional (default = ['email', 'id', 'firstname', 'lastname'])
            All the fields to request among the possible fields for the users.
            See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#user) for all possible fields.
        - first : int, optional (default = 100)
            Maximum number of users to return.
        - skip : int, optional (default = 0)
            Number of skipped users (they are ordered by creation date)
        - disable_tqdm : bool, (default = False)
        - as_generator: bool, (default = False)
            If True, a generator on the users is returned.

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.

        Examples
        -------
        >>> # List all users in my organization
        >>> organization = kili.organizations()
        >>> organization_id = organizations[0]['id]
        >>> kili.users(organization_id=organization_id)
        """
        if as_generator is False:
            warnings.warn("From 2022-05-18, the default return type will be a generator. Currently, the default return type is a list. \n"
                          "If you want to force the query return to be a list, you can already call this method with the argument as_generator=False",
                          DeprecationWarning)

        count_args = {"organization_id": organization_id}
        disable_tqdm = disable_tqdm or as_generator or (
            api_key or email) is not None
        payload_query = {
            'where': {
                'apiKey': api_key,
                'email': email,
                'organization': {
                    'id': organization_id,
                }
            }
        }

        users_generator = row_generator_from_paginated_calls(
            skip,
            first,
            self.count_users,
            count_args,
            self._query_users,
            payload_query,
            fields,
            disable_tqdm
        )

        if as_generator:
            return users_generator
        return list(users_generator)

    def _query_users(self,
                     skip: int,
                     first: int,
                     payload: dict,
                     fields: List[str]):

        payload.update({'skip': skip, 'first': first})
        _gql_users = gql_users(fragment_builder(fields, User))
        result = self.auth.client.execute(_gql_users, payload)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    @typechecked
    def count_users(self,
                    organization_id: Optional[str] = None):
        """
        Get user count based on a set of constraints

        Parameters
        ----------
        - organization_id : str, optional (default = None)

        Returns
        -------
        - the count of users whose organization ID matches the given ID
        """
        variables = {
            'where': {
                'organization': {
                    'id': organization_id,
                }
            }
        }
        result = self.auth.client.execute(GQL_USERS_COUNT, variables)
        return format_result('data', result)
