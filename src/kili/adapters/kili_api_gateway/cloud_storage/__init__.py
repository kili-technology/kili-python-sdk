"""Mixin extending Kili API Gateway class with Cloud Storage related operations."""

from typing import Dict, Generator

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.domain.cloud_storage import (
    DataConnectionFilters,
    DataConnectionId,
    DataIntegrationFilters,
)
from kili.domain.types import ListOrTuple

from .mappers import (
    add_data_connection_data_mapper,
    data_connection_where_mapper,
    data_integration_where_mapper,
)
from .operations import (
    GQL_COUNT_DATA_INTEGRATIONS,
    get_add_data_connection_query,
    get_data_connection_query,
    get_list_data_connections_query,
    get_list_data_integrations_query,
)
from .types import AddDataConnectionKiliAPIGatewayInput


class CloudStorageOperationMixin(BaseOperationMixin):
    """GraphQL Mixin extending GraphQL Gateway class with Cloud Storage related operations."""

    def list_data_integrations(
        self,
        data_integration_filters: DataIntegrationFilters,
        fields: ListOrTuple[str],
        options: QueryOptions,
    ) -> Generator[Dict, None, None]:
        """List data integrations."""
        fragment = fragment_builder(fields)
        query = get_list_data_integrations_query(fragment)
        where = data_integration_where_mapper(filters=data_integration_filters)
        return PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, "Retrieving data integrations", GQL_COUNT_DATA_INTEGRATIONS
        )

    def count_data_integrations(self, data_integration_filters: DataIntegrationFilters) -> int:
        """Count data integrations."""
        where = data_integration_where_mapper(filters=data_integration_filters)
        variables = {"where": where}
        result = self.graphql_client.execute(GQL_COUNT_DATA_INTEGRATIONS, variables)
        return result["data"]

    def list_data_connections(
        self,
        data_connection_filters: DataConnectionFilters,
        fields: ListOrTuple[str],
        options: QueryOptions,
    ) -> Generator[Dict, None, None]:
        """List data connections."""
        fragment = fragment_builder(fields)
        query = get_list_data_connections_query(fragment)
        where = data_connection_where_mapper(filters=data_connection_filters)
        return PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, "Retrieving data connections", GQL_COUNT_DATA_INTEGRATIONS
        )

    def get_data_connection(
        self, data_connection_id: DataConnectionId, fields: ListOrTuple[str]
    ) -> Dict:
        """Get data connection."""
        fragment = fragment_builder(fields)
        query = get_data_connection_query(fragment)
        result = self.graphql_client.execute(
            query=query, variables={"where": {"id": data_connection_id}}
        )
        return result["data"]

    def add_data_connection(
        self, data: AddDataConnectionKiliAPIGatewayInput, fields: ListOrTuple[str]
    ) -> Dict:
        """Add data connection to a project."""
        fragment = fragment_builder(fields)
        query = get_add_data_connection_query(fragment)
        variables = {"data": add_data_connection_data_mapper(data)}
        result = self.graphql_client.execute(query, variables)
        return result["data"]
