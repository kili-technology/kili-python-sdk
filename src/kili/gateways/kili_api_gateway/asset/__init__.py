"""Mixin extending Kili API Gateway class with Asset related operations."""


from typing import Callable, Dict, Generator, List, Optional

from kili.core.graphql.graphql_client import GraphQLClient
from kili.gateways.kili_api_gateway.asset.operations import (
    GQL_COUNT_ASSETS,
    GQL_CREATE_UPLOAD_BUCKET_SIGNED_URLS,
    get_asset_query,
)
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
        where: AssetWhere,
        fields: List[str],
        options: QueryOptions,
        post_call_function: Optional[Callable],
    ) -> Generator[Dict, None, None]:
        """List assets with given options."""
        fragment = fragment_builder(fields)
        query = get_asset_query(fragment)
        nb_elements_to_query = get_number_of_elements_to_query(
            self.graphql_client, where, options, GQL_COUNT_ASSETS
        )
        return PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, nb_elements_to_query, post_call_function
        )

    def count_assets(self, where: AssetWhere) -> int:
        """Send a GraphQL request calling countIssues resolver."""
        payload = {
            "where": where.build_gql_where(),
        }
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
