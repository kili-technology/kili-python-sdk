"""GraphQL payload data mappers for cloud storage operations."""

from typing import Dict

from kili.domain.cloud_storage import DataConnectionFilters, DataIntegrationFilters

from .types import (
    AddDataConnectionKiliAPIGatewayInput,
    DataConnectionComputeDifferencesKiliAPIGatewayInput,
)


def data_integration_where_mapper(filters: DataIntegrationFilters) -> Dict:
    """Build the GraphQL DataIntegrationWhere variable to be sent in an operation."""
    return {
        "status": filters.status,
        "id": filters.id,
        "name": filters.name,
        "organizationId": filters.organization_id,
        "platform": filters.platform,
    }


def data_connection_where_mapper(filters: DataConnectionFilters) -> Dict:
    """Build the GraphQL DataConnectionsWhere variable to be sent in an operation."""
    return {
        "projectId": filters.project_id,
        "integrationId": filters.integration_id,
    }


def add_data_connection_data_mapper(data: AddDataConnectionKiliAPIGatewayInput) -> Dict:
    """Build the GraphQL DataConnectionInput variable to be sent in an operation."""
    return {
        "projectId": data.project_id,
        "integrationId": data.integration_id,
        "isChecking": data.is_checking,
        "lastChecked": data.last_checked.isoformat(sep="T", timespec="milliseconds") + "Z",
        "selectedFolders": data.selected_folders,
    }


def compute_data_connection_difference_data_mapper(
    data: DataConnectionComputeDifferencesKiliAPIGatewayInput,
) -> Dict:
    """Build the GraphQL DataConnectionComputeDifferencesPayload variable."""
    return {
        "blobPaths": data.blob_paths,
        "warnings": data.warnings,
    }
