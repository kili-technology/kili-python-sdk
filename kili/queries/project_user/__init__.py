from typing import Optional
import warnings

from typeguard import typechecked

from ...helpers import Compatible, deprecate, format_result, fragment_builder
from .queries import gql_project_users, GQL_PROJECT_USERS_COUNT
from ...types import ProjectUser


class QueriesProjectUser:

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
    def project_users(self,
                      email: Optional[str] = None,
                      id: Optional[str] = None,
                      organization_id: Optional[str] = None,
                      project_id: Optional[str] = None,
                      fields: list = ['activated', 'id', 'role',
                                      'starred', 'user.email', 'user.id', 'user.name'],
                      first: int = 100,
                      skip: int = 0):
        """
        Return projects and their users (possibly with their KPIs) respecting a set of criteria

        Parameters
        ----------
        - email : str, optional (default = None)
        - organization_id : str, optional (default = None)
        - project_id : str, optional (default = None)
        - fields : list, optional (default = ['activated', 'id', 'role', 'starred', 'user.email', 'user.id', 'user.name'])
            All the fields to request among the possible fields for the projectUsers.
            See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#projectuser) for all possible fields.
        - first : int, optional (default = 100)
            Maximum number of users to return. Can only be between 0 and 100.
        - skip : int, optional (default = 0)
            Number of project users to skip

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.

        Examples
        -------
        >>> # Retrieve consensus marks of all users in project
        >>> playground.project_users(project_id=project_id, fields=['consensusMark', 'user.email'])
        """
        variables = {
            'first': first,
            'skip': skip,
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
        GQL_PROJECT_USERS = gql_project_users(
            fragment_builder(fields, ProjectUser))
        result = self.auth.client.execute(GQL_PROJECT_USERS, variables)
        return format_result('data', result)

    @typechecked
    def count_project_users(self, email: Optional[str] = None, id: Optional[str] = None, organization_id: Optional[str] = None, project_id: Optional[str] = None,):
        """
        Counts the number of projects and their users respecting a set of criteria

        Parameters
        ----------
        - email : str, optional (default = None)
        - organization_id : str, optional (default = None)
        - project_id : str, optional (default = None)

        Returns
        -------
        - a positive integer corresponding to the number of results of the query if it was successful, or an error message else.
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
