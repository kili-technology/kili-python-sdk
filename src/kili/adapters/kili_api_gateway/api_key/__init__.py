"""Mixin extending Kili API Gateway class with Asset related operations."""

from datetime import datetime
from typing import Dict, Generator

from kili import __version__
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
from kili.utils.logcontext import LogContext, log_call


class ApiKeyOperationMixin(BaseOperationMixin):
    """Mixin extending Kili API Gateway class with Assets related operations."""

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
        """Get the expiry date of a given api key.

        Returns it in the fomat `%Y-%m-%dT%H:%M:%S.%fZ`
        """
        payload = {"where": {"key": api_key}}
        result = self.graphql_client.execute(GQL_API_KEY_EXPIRY_DATE, payload)
        fetched_key = next(iter(result["data"] or []), None)
        if fetched_key is None:
            raise NotFound(f"Could not find api key {api_key}")
        return datetime.strptime(fetched_key["expiryDate"], r"%Y-%m-%dT%H:%M:%S.%fZ")

    @log_call
    def is_api_key_valid(self, api_key: str) -> bool:
        """Check that the api_key provided is valid.

        Note that this method does not rely on the GraphQL client, but on the HTTP client.
        It must stay this way since the GraphQL client might retry in case of 401 http error.
        """
        response = self.http_client.post(
            url=self.graphql_client.endpoint,
            data='{"query":"{ me { id email } }"}',
            timeout=30,
            headers={
                "Authorization": f"X-API-Key: {api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "apollographql-client-name": self.graphql_client.client_name.value,
                "apollographql-client-version": __version__,
                **LogContext(),
            },
        )
        return (
            response.status_code == 200  # noqa: PLR2004
            and "email" in response.text
            and "id" in response.text
        )
