"""GraphQL payload data mappers for cloud storage operations."""

from typing import Dict

from kili.adapters.kili_api_gateway.cloud_storage.types import DataIntegrationData
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
        "contentTypes": data.content_types,
    }


def integration_data_mapper(data: DataIntegrationData) -> Dict:
    """."""
    return {
        "allowedPaths": data.allowed_paths,
        "allowedProjects": data.allowed_projects,
        "awsAccessPointARN": data.aws_access_point_arn,
        "awsRoleARN": data.aws_role_arn,
        "awsRoleExternalId": data.aws_role_external_id,
        "azureConnectionURL": data.azure_connection_url,
        "azureIsUsingServiceCredentials": data.azure_is_using_service_credentials,
        "azureSASToken": data.azure_sas_token,
        "azureTenantId": data.azure_tenant_id,
        "gcpBucketName": data.gcp_bucket_name,
        "includeRootFiles": data.include_root_files,
        "internalProcessingAuthorized": data.internal_processing_authorized,
        "name": data.name,
        "organizationId": data.organization_id,
        "platform": data.platform,
        "status": data.status,
        "s3AccessKey": data.s3_access_key,
        "s3BucketName": data.s3_bucket_name,
        "s3Endpoint": data.s3_endpoint,
        "s3Region": data.s3_region,
        "s3SecretKey": data.s3_secret_key,
        "s3SessionToken": data.s3_session_token,
    }
