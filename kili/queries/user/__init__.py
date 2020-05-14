import warnings

from ...helpers import deprecate, format_result, fragment_builder
from .queries import gql_users
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

    @deprecate(
        """
        **New feature has been added : Query only the fields you want
        using the field argument, that accept a list of string organized like below.**
        The former default query with all fields is deprecated since 13/05/2020
        After 13/06/2020, the default queried fields will be : ['id', 'name', 'email']
        To fetch more fields, for example the organization fields, just add those :
        fields = ['id', 'name', 'email', 'organization.name', 'organization.city','activated']
        """)
    def users(self, email: str = None, organization_id: str = None, fields: list = ['email', 'id', 'name'], first: int = 100, skip: int = 0):
        """
        Get users

        Returns users whose email / organization id correspond to the given ones.

        Parameters
        ----------
        - email : str, optional (default = None)
        - organization_id : str, optional (default = None)
        - fields : list of string, optional (default = ['email', 'id', 'name'])
            All the fields to request among the possible fields for the users, default for None are the non-calculated fields)
            Possible fields : see https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#user
        - first : int, optional (default = 100)
            Maximum number of users to return. Can only be between 0 and 100.
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
        GQL_USERS = gql_users(fragment_builder(fields, User))
        result = self.auth.client.execute(GQL_USERS, variables)
        return format_result('data', result)

    def get_user(self, email: str):
        message = """This function is deprecated.
        To get users, use:
            playground.users(email=email, organization_id=organization_id)
        """
        warnings.warn(message, DeprecationWarning)
