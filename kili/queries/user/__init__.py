from typing import Optional
import warnings

from typeguard import typechecked

from ...helpers import Compatible, deprecate, format_result, fragment_builder
from .queries import gql_users, GQL_USERS_COUNT
from ...types import User


class QueriesUser:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @Compatible(['v1', 'v2'])
    @typechecked
    def users(self,
              api_key: Optional[str] = None,
              email: Optional[str] = None,
              organization_id: Optional[str] = None,
              fields: list = ['email', 'id', 'name'],
              first: int = 100,
              skip: int = 0):
        """
        Get users given a set of constraints

        Parameters
        ----------
        - api_key : str, optional (default = None) Query an user by its API KEY
        - email : str, optional (default = None)
        - organization_id : str, optional (default = None)
        - fields : list of string, optional (default = ['email', 'id', 'name'])
            All the fields to request among the possible fields for the users.
            See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#user) for all possible fields.
        - first : int, optional (default = 100)
            Maximum number of users to return. Can only be between 0 and 100.
        - skip : int, optional (default = 0)
            Number of skipped users (they are ordered by creation date)

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
        variables = {
            'first': first,
            'skip': skip,
            'where': {
                'apiKey': api_key,
                'email': email,
                'organization': {
                    'id': organization_id,
                }
            }
        }
        GQL_USERS = gql_users(fragment_builder(fields, User))
        result = self.auth.client.execute(GQL_USERS, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    @typechecked
    def count_users(self,
                    organization_id: Optional[str] = None):
        """
        Get users count given a set of constraints

        Parameters
        ----------
        - organization_id : str, optional (default = None)

        Returns
        -------
        - the count of users whose organization id correspond to the given one
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
