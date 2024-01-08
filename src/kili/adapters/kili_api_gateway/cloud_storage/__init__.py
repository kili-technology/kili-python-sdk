"""Mixin extending Kili API Gateway class with Cloud Storage related operations."""

from typing import Dict, Generator, Optional

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.cloud_storage.types import DataIntegrationData
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.domain.cloud_storage import (
    DataConnectionFilters,
    DataConnectionId,
    DataDifferenceType,
    DataIntegrationFilters,
    DataIntegrationId,
)
from kili.domain.types import ListOrTuple

from .mappers import (
    add_data_connection_data_mapper,
    compute_data_connection_difference_data_mapper,
    data_connection_where_mapper,
    data_integration_where_mapper,
    integration_data_mapper,
)
from .operations import (
    GQL_COUNT_DATA_INTEGRATIONS,
    GQL_DELETE_DATA_INTEGRATION,
    get_add_data_connection_mutation,
    get_compute_data_connection_differences_mutation,
    get_create_integration_mutation,
    get_data_connection_query,
    get_list_data_connections_query,
    get_list_data_integrations_query,
    get_update_integration_mutation,
    get_validate_data_connection_differences_mutation,
)
from .types import (
    AddDataConnectionKiliAPIGatewayInput,
    DataConnectionComputeDifferencesKiliAPIGatewayInput,
)


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
        query = get_add_data_connection_mutation(fragment)
        variables = {"data": add_data_connection_data_mapper(data)}
        result = self.graphql_client.execute(query, variables)
        return result["data"]

    def compute_data_connection_differences(
        self,
        data_connection_id: DataConnectionId,
        data: Optional[DataConnectionComputeDifferencesKiliAPIGatewayInput],
        fields: ListOrTuple[str],
    ) -> Dict:
        """Compute data connection differences."""
        fragment = fragment_builder(fields)
        query = get_compute_data_connection_differences_mutation(fragment)
        variables = {"where": {"id": data_connection_id}}
        if data is not None:
            variables["data"] = compute_data_connection_difference_data_mapper(data)
        result = self.graphql_client.execute(query, variables)
        return result["data"]

    def validate_data_connection_differences(
        self,
        data_connection_id: DataConnectionId,
        data_difference_type: DataDifferenceType,
        fields: ListOrTuple[str],
    ) -> Dict:
        """Validate data connection differences."""
        fragment = fragment_builder(fields)
        query = get_validate_data_connection_differences_mutation(fragment)
        variables = {"where": {"connectionId": data_connection_id, "type": data_difference_type}}
        result = self.graphql_client.execute(query, variables)
        return result["data"]

    def create_data_integration(self, data: DataIntegrationData, fields: ListOrTuple[str]) -> Dict:
        """Create a data integration."""
        fragment = fragment_builder(fields)
        query = get_create_integration_mutation(fragment)
        variables = {"data": integration_data_mapper(data)}
        result = self.graphql_client.execute(query, variables)
        return result["data"]

    def update_data_integration(
        self,
        data_integration_id: DataIntegrationId,
        data_integration_data: DataIntegrationData,
        fields: ListOrTuple[str],
    ) -> Dict:
        """Update a data integration."""
        fragment = fragment_builder(fields)
        query = get_update_integration_mutation(fragment)
        variables = {
            "data": integration_data_mapper(data=data_integration_data),
            "where": {"id": data_integration_id},
        }
        result = self.graphql_client.execute(query, variables)
        return result["data"]

    def delete_data_integration(self, data_integration_id: DataIntegrationId) -> str:
        """Delete a data integration."""
        variables = {"where": {"id": data_integration_id}}
        result = self.graphql_client.execute(GQL_DELETE_DATA_INTEGRATION, variables)
        return result["data"]
