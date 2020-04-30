import warnings

from ...helpers import format_result
from .queries import GQL_USERS


class QueriesUser:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    def users(self, email: str = None, organization_id: str = None, first: int = 100, skip: int = 0):
        """
        Get users

        Returns users whose email / organization id correspond to the given ones.

        Parameters
        ----------
        - email : str, optional (default = None)
        - organization_id : str, optional (default = None)
        - first : int, optional (default = 100)
            Maximum number of users to return
        - skip : int, optional (default = 0)
            Number of skipped users (they are ordered by creation date)

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        variables = {
            'first': first,
            'skip': skip,
            'where': {
                'email': email,
                'organization': {
                    'id': organization_id,
                }
            }
        }
        result = self.auth.client.execute(GQL_USERS, variables)
        return format_result('data', result)

    def get_user(self, email: str):
        message = """This function is deprecated.
        To get users, use:
            playground.users(email=email, organization_id=organization_id)
        """
        warnings.warn(message, DeprecationWarning)
