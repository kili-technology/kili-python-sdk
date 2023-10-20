"""Mixin extending Kili API Gateway class with Organization related operations."""

from typing import Dict, Generator

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.adapters.kili_api_gateway.organization.mappers import (
    map_create_organization_data,
    map_list_organizations_where,
    map_organization_metrics_where,
    map_update_organization_data,
    map_update_organization_where,
)
from kili.domain.organization import (
    OrganizationFilters,
    OrganizationId,
    OrganizationMetricsFilters,
    OrganizationToCreateInput,
    OrganizationToUpdateInput,
)
from kili.domain.types import ListOrTuple

from .operations import (
    COUNT_ORGANIZATIONS_QUERY,
    get_create_organization_mutation,
    get_get_organization_metrics_query,
    get_list_organizations_query,
    get_update_properties_in_organization_mutation,
)


class OrganizationOperationMixin(BaseOperationMixin):
    """GraphQL Mixin extending GraphQL Gateway class with Organization related operations."""

    def create_organization(
        self,
        organization: OrganizationToCreateInput,
    ) -> Dict:
        """Send a GraphQL request calling createOrganization resolver."""
        payload = {"data": map_create_organization_data(organization)}
        fragment = fragment_builder(["id"])
        result = self.graphql_client.execute(get_create_organization_mutation(fragment), payload)

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
        where = map_list_organizations_where(filters=filters)
        return PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, description, COUNT_ORGANIZATIONS_QUERY
        )

    def count_organizations(self, filters: OrganizationFilters) -> int:
        """Send a GraphQL request calling countOrganizations resolver."""
        where = map_list_organizations_where(filters=filters)
        payload = {"where": where}
        count_result = self.graphql_client.execute(COUNT_ORGANIZATIONS_QUERY, payload)
        count: int = count_result["data"]
        return count

    def get_organization_metrics(
        self, filters: OrganizationMetricsFilters, fields: ListOrTuple[str]
    ) -> Dict:
        """Send a GraphQL request calling organizationMetrics resolver."""
        where = map_organization_metrics_where(filters=filters)
        payload = {"where": where}
        fragment = fragment_builder(fields)
        result = self.graphql_client.execute(get_get_organization_metrics_query(fragment), payload)
        return result["data"]

    def update_organization(
        self,
        organization_id: OrganizationId,
        organization_data: OrganizationToUpdateInput,
    ) -> Dict:
        """Send a GraphQL request calling updateOrganization resolver."""
        data = map_update_organization_data(organization_data)
        where = map_update_organization_where(organization_id)
        payload = {"where": where, "data": data}
        fragment = fragment_builder(["id"])
        result = self.graphql_client.execute(
            get_update_properties_in_organization_mutation(fragment), payload
        )
        return result["data"]
