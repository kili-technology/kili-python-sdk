from ...helpers import format_result
from .queries import GQL_PROJECT_USERS, GQL_PROJECT_USERS_WITH_KPIS


class QueriesProjectUser:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    def project_users(self, email=None, id=None, organization_id=None, project_id=None, first=100, skip=0, with_kpis=False):
        """
        Return projects and their users (possibly with their KPIs)

        Parameters
        ----------
        - email : str, optional (default = None)
        - organization_id : str, optional (default = None)
        - project_id : str, optional (default = None)
        - first : int, optional (default = 100)
            Maximum number of users to return
        - skip : int, optional (default = 0)
            Number of project users to skip
        - with_kpis : bool, optional (default = False)
            Whether or not to compute kpis

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
        query = GQL_PROJECT_USERS_WITH_KPIS if with_kpis else GQL_PROJECT_USERS
        result = self.auth.client.execute(query, variables)
        return format_result('data', result)
