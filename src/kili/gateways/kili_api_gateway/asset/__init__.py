"""Mixin extending Kili API Gateway class with Asset related operations."""


from typing import Callable, List, Optional

from kili.core.graphql.graphql_client import GraphQLClient
from kili.gateways.kili_api_gateway.asset.operations import GQL_COUNT_ASSETS
from kili.gateways.kili_api_gateway.asset.types import AssetWhere
from kili.gateways.kili_api_gateway.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
    get_number_of_elements_to_query,
)


class AssetOperationMixin:
    """Mixin extending Kili API Gateway class with Assets related operations."""

    graphql_client: GraphQLClient

    def list_assets(
        self,
        fields: List[str],
        where: AssetWhere,
        options: QueryOptions,
        post_call_function: Optional[Callable],
    ):
        """List assets with given options."""
        query = fragment_builder(fields)
        nb_elements_to_query = get_number_of_elements_to_query(
            self.graphql_client, where, options, GQL_COUNT_ASSETS
        )
        return PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, nb_elements_to_query, post_call_function
        )

    def count_assets(self, asset_where: AssetWhere):
        """Send a GraphQL request calling countIssues resolver."""
        payload = {
            "where": asset_where.graphql_value,
        }
        count_result = self.graphql_client.execute(GQL_COUNT_ASSETS, payload)
        count: int = count_result["data"]
        return count
