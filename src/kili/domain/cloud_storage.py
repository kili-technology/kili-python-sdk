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

    id: Optional[DataIntegrationId]
    status: Optional[DataIntegrationStatus] = None
    name: Optional[str] = None
    organization_id: Optional[OrganizationId] = None
    platform: Optional[DataIntegrationPlatform] = None


@dataclass
class DataConnectionFilters:
    """Data Connection filters."""

    data_connection_id: Optional[DataConnectionId]
    project_id: Optional[ProjectId]
    integration_id: Optional[DataIntegrationId]
