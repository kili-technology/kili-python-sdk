"""Mixin extending Kili API Gateway class with Organization related operations."""

# from kili.adapters.kili_api_gateway.helpers.queries import (
#     PaginatedGraphQLQuery,
#     QueryOptions,
#     fragment_builder,
# from kili.adapters.kili_api_gateway.issue.operations import (
#     GQL_COUNT_ISSUES,
#     GQL_CREATE_ISSUES,


import tqdm

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.organization.mappers import map_organization_data
from kili.adapters.kili_api_gateway.organization.types import (
    KiliAPIGateWayCreateOrganizationInput,
)
from kili.domain.organization import Organization
from kili.entrypoints.mutations.organization.queries import GQL_CREATE_ORGANIZATION


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
