from ...helpers import Compatible, deprecate, format_result, fragment_builder
from .queries import gql_project_users
from ...types import ProjectUser
import warnings


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
    def project_users(self,
                      email: str = None,
                      id: str = None,
                      organization_id: str = None,
                      project_id: str = None,
                      fields: list = ['activated', 'id', 'role', 'starred', 'user.email', 'user.id', 'user.name'],
                      first: int = 100,
                      skip: int = 0):
        """
        Return projects and their users (possibly with their KPIs)

        Parameters
        ----------
        - email : str, optional (default = None)
        - organization_id : str, optional (default = None)
        - project_id : str, optional (default = None)
        - fields : list, optional (default = ['activated', 'id', 'role', 'starred', 'user.email', 'user.id', 'user.name'])
            All the fields to request among the possible fields for the projectUsers, default for None are the non-calculated fields)
            Possible fields : see https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#projectuser
        - first : int, optional (default = 100)
            Maximum number of users to return. Can only be between 0 and 100.
        - skip : int, optional (default = 0)
            Number of project users to skip

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
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
