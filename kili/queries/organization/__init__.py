import warnings

from ...helpers import format_result
from .queries import GQL_ORGANIZATIONS


class QueriesOrganization:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    def organizations(self, email: str = None, organization_id: str = None, first: int = 100, skip: int = 0):
        """
        Get organizations

        Returns users whose email / organization id correspond to the given ones.

        Parameters
        ----------
        - email : str, optional (default = None)
        - organization_id : str, optional (default = None)
        - first : int, optional (default = 100)
            Maximum number of organizations to return
        - skip : int, optional (default = 0)
            Number of skipped organizations (they are ordered by creation date)

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        variables = {
            'first': first,
            'skip': skip,
            'where': {
                'id': organization_id,
                'user': {
                    'email': email,
                }
            }
        }
        result = self.auth.client.execute(GQL_ORGANIZATIONS, variables)
        return format_result('data', result)
