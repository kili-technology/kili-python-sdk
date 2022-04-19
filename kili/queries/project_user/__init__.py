"""
Project user queries
"""

from typing import Generator, List, Optional, Union
import warnings

from typeguard import typechecked


from ...helpers import Compatible, deprecate, format_result, fragment_builder
from .queries import gql_project_users, GQL_PROJECT_USERS_COUNT
from ...types import ProjectUser
from ...utils import row_generator_from_paginated_calls


class QueriesProjectUser:
    """
    Set of ProjectUser queries
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

    # pylint: disable=dangerous-default-value,invalid-name
    @Compatible(['v1', 'v2'])
    @typechecked
    def project_users(self,
                      email: Optional[str] = None,
                      id: Optional[str] = None,  # pylint: disable=redefined-builtin
                      organization_id: Optional[str] = None,
                      project_id: Optional[str] = None,
                      fields: list = ['activated', 'id', 'role',
                                      'starred', 'user.email', 'user.id'],
                      first: int = 100,
                      skip: int = 0,
                      disable_tqdm: bool = False,
                      as_generator: bool = False) -> Union[List[dict], Generator[dict, None, None]]:
        # pylint: disable=line-too-long
        """
        Return project users (possibly with their KPIs) that match a set of criteria


        Parameters
        ----------
        - email : str, optional (default = None)
        - organization_id : str, optional (default = None)
        - project_id : str, optional (default = None)
        - fields : list, optional (default = ['activated', 'id', 'role', 'starred',
            'user.email', 'user.id'])
            All the fields to request among the possible fields for the projectUsers.
            See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#projectuser) for all possible fields.
        - first : int, optional (default = 100)
            Maximum number of users to return
        - skip : int, optional (default = 0)
            Number of project users to skip
        - disable_tqdm : bool, (default = False)
        - as_generator: bool, (default = False)
            If True, a generator on the project users is returned.

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.

        Examples
        -------
        >>> # Retrieve consensus marks of all users in project
        >>> kili.project_users(project_id=project_id, fields=['consensusMark', 'user.email'])
        """
        if as_generator is False:
            warnings.warn("From 2022-05-18, the default return type will be a generator. Currently, the default return type is a list. \n"
                          "If you want to force the query return to be a list, you can already call this method with the argument as_generator=False",
                          DeprecationWarning)

        count_args = {"email": email,
                      "id": id,
                      "organization_id": organization_id,
                      "project_id": project_id}
        disable_tqdm = disable_tqdm or as_generator
        payload_query = {
            'where': {
                'id': id,
                'project': {
                    'id': project_id,
                },
                'user': {
                    'email': email,
                    'organization': {
                        'id': organization_id,
                    }
                },
            }
        }

        project_users_generator = row_generator_from_paginated_calls(
            skip,
            first,
            self.count_project_users,
            count_args,
            self._query_project_users,
            payload_query,
            fields,
            disable_tqdm
        )

        if as_generator:
            return project_users_generator
        return list(project_users_generator)

    def _query_project_users(self,
                             skip: int,
                             first: int,
                             payload: dict,
                             fields: List[str]):

        payload.update({'skip': skip, 'first': first})
        _gql_project_users = gql_project_users(
            fragment_builder(fields, ProjectUser))
        result = self.auth.client.execute(_gql_project_users, payload)
        return format_result('data', result)

    # pylint: disable=invalid-name
    @typechecked
    def count_project_users(
            self,
            email: Optional[str] = None,
            id: Optional[str] = None,  # pylint: disable=redefined-builtin
            organization_id: Optional[str] = None,
            project_id: Optional[str] = None):
        """
        Counts the number of projects and their users that match a set of criteria

        Parameters
        ----------
        - email : str, optional (default = None)
        - organization_id : str, optional (default = None)
        - project_id : str, optional (default = None)

        Returns
        -------
        - a positive integer corresponding to the number of results of the query
            if it was successful, or an error message else.
        """
        variables = {
            'where': {
                'id': id,
                'project': {
                    'id': project_id,
                },
                'user': {
                    'email': email,
                    'organization': {
                        'id': organization_id,
                    }
                },
            }
        }
        result = self.auth.client.execute(GQL_PROJECT_USERS_COUNT, variables)
        count = format_result('data', result)
        return count
