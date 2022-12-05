"""Organization queries."""

from datetime import datetime
from typing import Generator, List, Optional, Union

from typeguard import typechecked

from ...helpers import format_result, fragment_builder
from ...types import Organization
from ...utils.pagination import row_generator_from_paginated_calls
from .queries import (
    GQL_ORGANIZATION_METRICS,
    GQL_ORGANIZATIONS_COUNT,
    gql_organizations,
)


class QueriesOrganization:
    """
    Set of Organization queries
    """

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    # pylint: disable=dangerous-default-value
    @typechecked
    def organizations(
        self,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: List[str] = ["id", "name"],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        as_generator: bool = False,
    ) -> Union[List[dict], Generator[dict, None, None]]:
        # pylint: disable=line-too-long
        """Get a generator or a list of organizations that match a set of criteria.

        Args:
            email : Email of a user of the organization
            organization_id : Identifier of the organization
            fields: All the fields to request among the possible fields for the organizations.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#organization) for all possible fields.
            first: Maximum number of organizations to return.
            skip: Number of skipped organizations (they are ordered by creation date)
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the organizations is returned.

        Returns:
            A result object which contains the query if it was successful,
                or an error message.

        Examples:
            >>> kili.organizations(organization_id=organization_id, fields=['users.email'])
            [{'users': [{'email': 'john@doe.com'}]}]
        """

        count_args = {"email": email, "organization_id": organization_id}
        disable_tqdm = disable_tqdm or as_generator

        payload_query = {
            "where": {
                "id": organization_id,
                "user": {
                    "email": email,
                },
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
            disable_tqdm,
        )

        if as_generator:
            return organizations_generator
        return list(organizations_generator)

    def _query_organizations(self, skip: int, first: int, payload: dict, fields: List[str]):
        payload.update({"skip": skip, "first": first})
        _gql_organizations = gql_organizations(fragment_builder(fields, Organization))
        result = self.auth.client.execute(_gql_organizations, payload)
        return format_result("data", result)

    @typechecked
    def count_organizations(
        self, email: Optional[str] = None, organization_id: Optional[str] = None
    ) -> int:
        """Count organizations that match a set of criteria.

        Args:
            email: Email of a user of the organization
            organization_id: Identifier of the organization

        Returns:
            A result object which contains the query if it was successful,
                or an error message.
        """
        variables = {
            "where": {
                "id": organization_id,
                "user": {
                    "email": email,
                },
            }
        }
        result = self.auth.client.execute(GQL_ORGANIZATIONS_COUNT, variables)
        return format_result("data", result, int)

    @typechecked
    def organization_metrics(
        self,
        organization_id: str,
        start_date: datetime,
        end_date: datetime,
    ):
        """Get organization metrics.

        Args:
            organization_id: Identifier of the organization
            start_date: Start date of the metrics computation
            end_date: End date of the metrics computation

        Returns:
            A result object which contains the query if it was successful,
                or an error message.
        """
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = datetime.now()
        variables = {
            "where": {
                "organizationId": organization_id,
                "startDate": start_date.isoformat(sep="T", timespec="milliseconds") + "Z",
                "endDate": end_date.isoformat(sep="T", timespec="milliseconds") + "Z",
            }
        }
        result = self.auth.client.execute(GQL_ORGANIZATION_METRICS, variables)
        return format_result("data", result)
