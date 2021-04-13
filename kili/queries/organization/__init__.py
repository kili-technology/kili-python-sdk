from typing import Optional
import warnings

from typeguard import typechecked

from ...helpers import Compatible, deprecate, format_result, fragment_builder
from .queries import gql_organizations, GQL_ORGANIZATIONS_COUNT
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

    @Compatible(['v1', 'v2'])
    @typechecked
    def organizations(self, email: Optional[str] = None, 
            organization_id: Optional[str] = None, fields: list = ['id', 'name'], 
            first: int = 100, skip: int = 0):
        """
        Get organizations respecting a set of criteria

        Returns all organizations:
        - with a given organization id
        - containing a user with a given email

        Parameters
        ----------
        - email : str, optional (default = None)
        - organization_id : str, optional (default = None)
        - fields : list of string, optional (default = ['id', 'name'])
            All the fields to request among the possible fields for the organizations.
            See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#organization) for all possible fields.
        - first : int, optional (default = 100)
            Maximum number of organizations to return
        - skip : int, optional (default = 0)
            Number of skipped organizations (they are ordered by creation date)

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.

        Examples
        -------
        >>> playground.organizations(organization_id=organization_id, fields=['users.email'])
        [{'users': [{'email': 'john@doe.com'}]}]
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

    @Compatible(['v2'])
    @typechecked
    def count_organizations(self, email: Optional[str] = None, 
            organization_id: Optional[str] = None):
        """
        Count organizations respecting a set of criteria

        Parameters
        ----------
        - email : str, optional (default = None)
        - organization_id : str, optional (default = None)

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        variables = {
            'where': {
                'id': organization_id,
                'user': {
                    'email': email,
                }
            }
        }
        result = self.auth.client.execute(GQL_ORGANIZATIONS_COUNT, variables)
        return format_result('data', result)
