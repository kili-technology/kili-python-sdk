"""Types for the Cloud storage related Kili API gateway functions."""

from dataclasses import dataclass
from typing import Optional

from kili.domain.cloud_storage import (
    DataIntegrationId,
    DataIntegrationPlatform,
    DataIntegrationStatus,
)
from kili.domain.organization import OrganizationId
from kili.domain.project import ProjectId


@dataclass
class AddDataConnectionKiliAPIGatewayInput:
    """Add data connection input data for Kili API Gateway."""

    exclude: Optional[list[str]]
    include: Optional[list[str]]
    integration_id: DataIntegrationId
    prefix: Optional[str]
    project_id: ProjectId
    selected_folders: Optional[list[str]]


@dataclass
class DataConnectionComputeDifferencesKiliAPIGatewayInput:
    """Data connection compute differences input data for Kili API Gateway."""

    blob_paths: list[str]
    warnings: list[str]
    content_types: list[str]


@dataclass
class DataIntegrationData:
    """Data integration input data."""

    allowed_paths: Optional[list[str]]
    allowed_projects: Optional[list[str]]
    aws_access_point_arn: Optional[str]
    aws_role_arn: Optional[str]
    aws_role_external_id: Optional[str]
    azure_connection_url: Optional[str]
    azure_is_using_service_credentials: Optional[bool]
    azure_sas_token: Optional[str]
    azure_tenant_id: Optional[str]
    gcp_bucket_name: Optional[str]
    include_root_files: Optional[str]
    internal_processing_authorized: Optional[str]
    name: Optional[str]
    organization_id: Optional[OrganizationId]
    platform: Optional[DataIntegrationPlatform]
    s3_access_key: Optional[str]
    s3_bucket_name: Optional[str]
    s3_endpoint: Optional[str]
    s3_region: Optional[str]
    s3_secret_key: Optional[str]
    s3_session_token: Optional[str]
    status: Optional[DataIntegrationStatus]
