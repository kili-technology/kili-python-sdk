"""Mixin extending Kili API Gateway class with Api Keys related operations."""

from datetime import datetime
from typing import Dict, Generator

from kili.adapters.kili_api_gateway.api_key.mappers import api_key_where_mapper
from kili.adapters.kili_api_gateway.api_key.operations import (
    GQL_API_KEY_EXPIRY_DATE,
    GQL_COUNT_API_KEYS,
    get_api_keys_query,
)
from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.domain.api_key import ApiKeyFilters
from kili.domain.types import ListOrTuple
from kili.exceptions import NotFound


class ApiKeyOperationMixin(BaseOperationMixin):
    """Mixin extending Kili API Gateway class with API Keys related operations."""

    def list_api_keys(
        self,
        filters: ApiKeyFilters,
        fields: ListOrTuple[str],
        options: QueryOptions,
    ) -> Generator[Dict, None, None]:
        """List assets with given options."""
        fragment = fragment_builder(fields)
        query = get_api_keys_query(fragment)
        where = api_key_where_mapper(filters)
        return PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, "Retrieving api keys", GQL_COUNT_API_KEYS
        )

    def count_api_keys(self, filters: ApiKeyFilters) -> int:
        """Send a GraphQL request calling countIssues resolver."""
        where = api_key_where_mapper(filters)
        payload = {"where": where}
        count_result = self.graphql_client.execute(GQL_COUNT_API_KEYS, payload)
        count: int = count_result["data"]
        return count

    def get_api_key_expiry_date(self, api_key: str) -> datetime:
        """Get the expiry date of a given api key as a datetime type."""
        payload = {"where": {"key": api_key}}
        result = self.graphql_client.execute(GQL_API_KEY_EXPIRY_DATE, payload)
        fetched_key = next(iter(result["data"] or []), None)
        if fetched_key is None:
            raise NotFound(f"Could not find api key {api_key}")
        return datetime.strptime(fetched_key["expiryDate"], r"%Y-%m-%dT%H:%M:%S.%fZ")
