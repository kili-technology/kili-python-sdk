import warnings

from ...helpers import deprecate, format_result, fragment_builder
from .queries import gql_organizations
from ...types import Organization


class QueriesOrganization:

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
        After 13/06/2020, the default queried fields will be : ['id', 'name']
        To fetch more fields, just add those :
        fields = ['id', 'name','address','zipCode','city','country']
        """)
    def organizations(self, email: str = None, organization_id: str = None, fields: list = ['id', 'name'], first: int = 100, skip: int = 0):
        """
        Get organizations

        Returns users whose email / organization id correspond to the given ones.

        Parameters
        ----------
        - email : str, optional (default = None)
        - organization_id : str, optional (default = None)
        - fields : list of string, optional (default = ['id', 'name'])
            All the fields to request among the possible fields for the organizations, default for None are the non-calculated fields)
            Possible fields : see https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#organization
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
        GQL_ORGANIZATIONS = gql_organizations(
            fragment_builder(fields, Organization))
        result = self.auth.client.execute(GQL_ORGANIZATIONS, variables)
        return format_result('data', result)
