"""Mixin extending Kili API Gateway class with Organization related operations."""

from collections.abc import Generator

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
    map_organization_usage_by_project_where,
    map_organization_usage_where,
    map_update_organization_data,
    map_update_organization_where,
)
from kili.domain.organization import (
    OrganizationFilters,
    OrganizationId,
    OrganizationMetricsFilters,
    OrganizationToCreateInput,
    OrganizationToUpdateInput,
    OrganizationUsageByProjectFilters,
    OrganizationUsageFilters,
)
from kili.domain.types import ListOrTuple
from kili.utils.tqdm import tqdm

from .operations import (
    COUNT_ORGANIZATIONS_QUERY,
    GET_ORGANIZATION_USAGE_QUERY,
    LIST_ORGANIZATION_USAGE_BY_PROJECT_QUERY,
    get_create_organization_mutation,
    get_get_organization_metrics_query,
    get_list_organizations_query,
    get_update_properties_in_organization_mutation,
)

# The most projects organizationMetricsAnalyticsByProject returns in one page
USAGE_BY_PROJECT_PAGE_SIZE = 50


class OrganizationOperationMixin(BaseOperationMixin):
    """GraphQL Mixin extending GraphQL Gateway class with Organization related operations."""

    def create_organization(
        self,
        organization: OrganizationToCreateInput,
    ) -> dict:
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
    ) -> Generator[dict, None, None]:
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
    ) -> dict:
        """Send a GraphQL request calling organizationMetrics resolver."""
        where = map_organization_metrics_where(filters=filters)
        payload = {"where": where}
        fragment = fragment_builder(fields)
        result = self.graphql_client.execute(get_get_organization_metrics_query(fragment), payload)
        return result["data"]

    def get_organization_usage(self, filters: OrganizationUsageFilters) -> list[dict]:
        """Send a GraphQL request calling organizationMetricsAnalytics resolver."""
        payload = {"where": map_organization_usage_where(filters)}
        result = self.graphql_client.execute(GET_ORGANIZATION_USAGE_QUERY, payload)
        return result["data"] or []

    def list_organization_usage_by_project(
        self, filters: OrganizationUsageByProjectFilters, options: QueryOptions
    ) -> Generator[dict, None, None]:
        """Send a series of GraphQL requests calling organizationMetricsAnalyticsByProject resolver.

        Its answer is a page and the total count, which PaginatedGraphQLQuery does not read.
        """
        where = map_organization_usage_by_project_where(filters)
        skip = options.skip
        retrieved = 0
        with tqdm(disable=options.disable_tqdm, desc="Retrieving usage by project") as pbar:
            while options.first is None or retrieved < options.first:
                first = USAGE_BY_PROJECT_PAGE_SIZE
                if options.first is not None:
                    first = min(first, options.first - retrieved)
                page = self.graphql_client.execute(
                    LIST_ORGANIZATION_USAGE_BY_PROJECT_QUERY,
                    {"where": where, "first": first, "skip": skip},
                )["data"]
                projects = page["data"] or []
                if pbar.total is None:
                    pbar.total = max(page["totalCount"] - options.skip, 0)
                yield from projects
                pbar.update(len(projects))
                retrieved += len(projects)
                skip += len(projects)
                if len(projects) < first or skip >= page["totalCount"]:
                    break

    def update_organization(
        self,
        organization_id: OrganizationId,
        organization_data: OrganizationToUpdateInput,
    ) -> dict:
        """Send a GraphQL request calling updateOrganization resolver."""
        data = map_update_organization_data(organization_data)
        where = map_update_organization_where(organization_id)
        payload = {"where": where, "data": data}
        fragment = fragment_builder(["id"])
        result = self.graphql_client.execute(
            get_update_properties_in_organization_mutation(fragment), payload
        )
        return result["data"]
