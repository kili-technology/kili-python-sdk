"""Mixin extending Kili API Gateway class with Asset related operations."""


from typing import Callable, Dict, Generator, List, Optional, Sequence

from kili.adapters.kili_api_gateway.asset.mappers import asset_where_mapper
from kili.adapters.kili_api_gateway.asset.operations import (
    GQL_COUNT_ASSETS,
    GQL_CREATE_UPLOAD_BUCKET_SIGNED_URLS,
    get_asset_query,
)
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
    get_number_of_elements_to_query,
)
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.asset import AssetFilters


class AssetOperationMixin:
    """Mixin extending Kili API Gateway class with Assets related operations."""

    graphql_client: GraphQLClient

    def list_assets(
        self,
        filters: AssetFilters,
        fields: Sequence[str],
        options: QueryOptions,
        post_call_function: Optional[Callable],
    ) -> Generator[Dict, None, None]:
        """List assets with given options."""
        fragment = fragment_builder(fields)
        query = get_asset_query(fragment)
        where = asset_where_mapper(filters)
        nb_elements_to_query = get_number_of_elements_to_query(
            self.graphql_client, GQL_COUNT_ASSETS, where, options
        )
        return PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, "Retrieving assets", nb_elements_to_query, post_call_function
        )

    def count_assets(self, filters: AssetFilters) -> int:
        """Send a GraphQL request calling countIssues resolver."""
        where = asset_where_mapper(filters)
        payload = {"where": where}
        count_result = self.graphql_client.execute(GQL_COUNT_ASSETS, payload)
        count: int = count_result["data"]
        return count

    def create_upload_bucket_signed_urls(self, file_paths: List[str]) -> List[str]:
        """Send a GraphQL request calling createUploadBucketSignedUrls resolver."""
        payload = {
            "filePaths": file_paths,
        }
        urls_response = self.graphql_client.execute(GQL_CREATE_UPLOAD_BUCKET_SIGNED_URLS, payload)
        return urls_response["urls"]
