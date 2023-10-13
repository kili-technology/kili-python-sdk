"""Mixin extending Kili API Gateway class with Organization related operations."""

from typing import Dict, Generator, Optional

import tqdm

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.adapters.kili_api_gateway.organization.mappers import (
    map_organization_data,
    map_organization_metrics_where,
    map_organization_where,
)
from kili.adapters.kili_api_gateway.organization.types import (
    KiliAPIGateWayCreateOrganizationInput,
)
from kili.domain.organization import (
    Organization,
    OrganizationFilters,
    OrganizationMetricsFilters,
)
from kili.domain.types import ListOrTuple

from .operations import (
    ORGANIZATION_FRAGMENT,
    get_count_organizations_query,
    get_create_organization_mutation,
    get_list_organizations_query,
    get_organization_metrics_query,
)


class OrganizationOperationMixin(BaseOperationMixin):
    """GraphQL Mixin extending GraphQL Gateway class with Organization related operations."""

    def create_organization(
        self,
        organization: KiliAPIGateWayCreateOrganizationInput,
        description: str,
        disable_tqdm: bool,
    ) -> Organization:
        """Send a GraphQL request calling createOrganization resolver."""
        with tqdm.tqdm(total=1, desc=description, disable=disable_tqdm) as pbar:
            payload = map_organization_data(organization)
            result = self.graphql_client.execute(
                get_create_organization_mutation(ORGANIZATION_FRAGMENT), payload
            )
            pbar.update(1)

        return result["data"]

    def list_organizations(
        self,
        filters: OrganizationFilters,
        fields: ListOrTuple[str],
        description: str,
        options: QueryOptions,
    ) -> Generator[Dict, None, None]:
        """Send a series of GraphQL request calling organizations resolver."""
        fragment = fragment_builder(fields)
        query = get_list_organizations_query(fragment)
        where = map_organization_where(filters=filters)
        return PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, description, get_count_organizations_query()
        )

    def count_organizations(self, filters: OrganizationFilters) -> int:
        """Send a GraphQL request calling countOrganizations resolver."""
        where = map_organization_where(filters=filters)
        payload = {"where": where}
        count_result = self.graphql_client.execute(get_count_organizations_query(), payload)
        count: int = count_result["data"]
        return count

    def get_organization_metrics(
        self, filters: OrganizationMetricsFilters, description: str, disable_tqdm: Optional[bool]
    ) -> Dict:
        """Send a GraphQL request calling organizationMetrics resolver."""
        with tqdm.tqdm(total=1, desc=description, disable=disable_tqdm) as pbar:
            where = map_organization_metrics_where(filters=filters)
            payload = {"where": where}
            result = self.graphql_client.execute(get_organization_metrics_query(), payload)
            pbar.update(1)
        return result["data"]
