"""
Organization queries
"""

from datetime import datetime
from typing import Generator, List, Optional, Union
import warnings

from typeguard import typechecked


from ...helpers import Compatible, deprecate, format_result, fragment_builder
from .queries import gql_organizations, GQL_ORGANIZATIONS_COUNT, GQL_ORGANIZATION_METRICS
from ...types import Organization
from ...utils import row_generator_from_paginated_calls


class QueriesOrganization:
    """
    Set of Organization queries
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

    # pylint: disable=dangerous-default-value
    @Compatible(['v1', 'v2'])
    @typechecked
    def organizations(
            self,
            email: Optional[str] = None,
            organization_id: Optional[str] = None,
            fields: list = ['id', 'name'],
            first: int = 100,
            skip: int = 0,
            disable_tqdm: bool = False,
            as_generator: bool = False) -> Union[List[dict], Generator[dict, None, None]]:
        # pylint: disable=line-too-long
        """
        Get a generator or a list of organizations that match a set of criteria

        Returns all organizations:
        - with a given organization id
        - containing a user with a given email

        Parameters
        ----------
        - email : str, optional (default = None)
        - organization_id : str, optional (default = None)
        - fields : list of string, optional (default = ['id', 'name'])
            All the fields to request among the possible fields for the organizations.
            See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#organization)
                for all possible fields.
        - first : int, optional (default = 100)
            Maximum number of organizations to return
        - skip : int, optional (default = 0)
            Number of skipped organizations (they are ordered by creation date)
        - disable_tqdm : bool, (default = False)
        - as_generator: bool, (default = False)
            If True, a generator on the organizations is returned.

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.

        Examples
        -------
        >>> kili.organizations(organization_id=organization_id, fields=['users.email'])
        [{'users': [{'email': 'john@doe.com'}]}]
        """
        if as_generator is False:
            warnings.warn("From 2022-05-18, the default return type will be a generator. Currently, the default return type is a list. \n"
                          "If you want to force the query return to be a list, you can already call this method with the argument as_generator=False",
                          DeprecationWarning)

        count_args = {"email": email, "organization_id": organization_id}
        disable_tqdm = disable_tqdm or as_generator

        payload_query = {
            'where': {
                'id': organization_id,
                'user': {
                    'email': email,
                }
            }
        }

        organizations_generator = row_generator_from_paginated_calls(
            skip,
            first,
            self.count_organizations,
            count_args,
            self._query_organizations,
            payload_query,
            fields,
            disable_tqdm
        )

        if as_generator:
            return organizations_generator
        return list(organizations_generator)

    def _query_organizations(self,
                             skip: int,
                             first: int,
                             payload: dict,
                             fields: List[str]):

        payload.update({'skip': skip, 'first': first})
        _gql_organizations = gql_organizations(
            fragment_builder(fields, Organization))
        result = self.auth.client.execute(_gql_organizations, payload)
        return format_result('data', result)

    @Compatible(['v2'])
    @typechecked
    def count_organizations(
            self,
            email: Optional[str] = None,
            organization_id: Optional[str] = None):
        """
        Count organizations that match a set of criteria

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

    @Compatible(['v2'])
    @typechecked
    def organization_metrics(self, organization_id: str = None,
                             start_date: datetime = datetime.now(),
                             end_date: datetime = datetime.now()):
        """
        Get organization metrics

        Parameters
        ----------
        - organization_id : str
        - start_date : datetime
        - end_date : datetime

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        variables = {
            'where': {
                'organizationId': organization_id,
                'startDate': start_date.isoformat(sep='T', timespec='milliseconds') + 'Z',
                'endDate': end_date.isoformat(sep='T', timespec='milliseconds') + 'Z',
            }
        }
        result = self.auth.client.execute(GQL_ORGANIZATION_METRICS, variables)
        return format_result('data', result)
