"""Mixin extending Kili API Gateway class with Organization related operations."""

from typing import Dict, Generator

import tqdm

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.adapters.kili_api_gateway.organization.mappers import (
    map_organization_data,
    map_organization_where,
)
from kili.adapters.kili_api_gateway.organization.types import (
    KiliAPIGateWayCreateOrganizationInput,
)
from kili.domain.organization import Organization, OrganizationFilters
from kili.domain.types import ListOrTuple

from .operations import (
    GQL_CREATE_ORGANIZATION,
    get_count_organizations_query,
    get_list_organizations_query,
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
            result = self.graphql_client.execute(GQL_CREATE_ORGANIZATION, payload)
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
