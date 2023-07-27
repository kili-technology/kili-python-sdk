"""Organization queries."""

from datetime import datetime
from typing import Dict, Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.core.graphql import QueryOptions
from kili.core.graphql.graphql_client import GraphQLClient
from kili.core.graphql.operations.organization.queries import (
    OrganizationMetricsWhere,
    OrganizationQuery,
    OrganizationWhere,
)
from kili.core.helpers import disable_tqdm_if_as_generator
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class QueriesOrganization(BaseOperationEntrypointMixin):
    """Set of Organization queries."""

    graphql_client: GraphQLClient

    # pylint: disable=too-many-arguments,dangerous-default-value

    @overload
    def organizations(
        self,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: List[str] = ["id", "name"],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def organizations(
        self,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: List[str] = ["id", "name"],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @typechecked
    def organizations(
        self,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: List[str] = ["id", "name"],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        # pylint: disable=line-too-long
        """Get a generator or a list of organizations that match a set of criteria.

        Args:
            email: Email of a user of the organization
            organization_id: Identifier of the organization
            fields: All the fields to request among the possible fields for the organizations.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#organization) for all possible fields.
            first: Maximum number of organizations to return.
            skip: Number of skipped organizations (they are ordered by creation date)
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the organizations is returned.

        Returns:
            An iterable of organizations.

        Examples:
            >>> kili.organizations(organization_id=organization_id, fields=['users.email'])
            [{'users': [{'email': 'john@doe.com'}]}]
        """
        where = OrganizationWhere(
            email=email,
            organization_id=organization_id,
        )
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        organizations_gen = OrganizationQuery(self.graphql_client, self.http_client)(
            where, fields, options
        )

        if as_generator:
            return organizations_gen
        return list(organizations_gen)

    @typechecked
    def count_organizations(
        self, email: Optional[str] = None, organization_id: Optional[str] = None
    ) -> int:
        """Count organizations that match a set of criteria.

        Args:
            email: Email of a user of the organization
            organization_id: Identifier of the organization

        Returns:
            An integer corresponding to the number of organizations that match the criteria.
        """
        where = OrganizationWhere(
            email=email,
            organization_id=organization_id,
        )
        return OrganizationQuery(self.graphql_client, self.http_client).count(where)

    @typechecked
    def organization_metrics(
        self,
        organization_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict:
        """Get organization metrics.

        Args:
            organization_id: Identifier of the organization
            start_date: Start date of the metrics computation
            end_date: End date of the metrics computation

        Returns:
            A dictionary containing the metrics of the organization.
        """
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = datetime.now()
        where = OrganizationMetricsWhere(
            organization_id=organization_id, start_date=start_date, end_date=end_date
        )
        return OrganizationQuery(self.graphql_client, self.http_client).metrics(where)
