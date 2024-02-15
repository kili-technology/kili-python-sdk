"""Types for the Cloud storage related Kili API gateway functions."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

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

    is_checking: bool
    integration_id: DataIntegrationId
    last_checked: datetime
    project_id: ProjectId
    selected_folders: Optional[List[str]]


@dataclass
class DataConnectionComputeDifferencesKiliAPIGatewayInput:
    """Data connection compute differences input data for Kili API Gateway."""

    blob_paths: List[str]
    warnings: List[str]
    content_types: List[str]


@dataclass
class DataIntegrationData:
    """Data integration input data."""

    allowed_paths: Optional[List[str]]
    allowed_projects: Optional[List[str]]
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
    status: Optional[DataIntegrationStatus]
    s3_access_key: Optional[str]
    s3_bucket_name: Optional[str]
    s3_endpoint: Optional[str]
    s3_region: Optional[str]
    s3_secret_key: Optional[str]
    s3_session_token: Optional[str]
