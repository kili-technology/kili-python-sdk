"""Cloud Storage domain."""
from dataclasses import dataclass
from typing import Literal, NewType, Optional

from .organization import OrganizationId
from .project import ProjectId

DataIntegrationId = NewType("DataIntegrationId", str)
DataConnectionId = NewType("DataConnectionId", str)

DataIntegrationPlatform = Literal["AWS", "Azure", "GCP"]


DataIntegrationStatus = Literal["CONNECTED", "DISCONNECTED", "CHECKING"]


@dataclass
class DataIntegrationFilters:
    """Data Integration filters."""

    status: Optional[DataIntegrationStatus]
    id: Optional[DataIntegrationId]
    name: Optional[str]
    organization_id: Optional[OrganizationId]
    platform: Optional[DataIntegrationPlatform]


@dataclass
class DataConnectionFilters:
    """Data Connection filters."""

    data_connection_id: Optional[DataConnectionId]
    project_id: Optional[ProjectId]
    integration_id: Optional[DataIntegrationId]
