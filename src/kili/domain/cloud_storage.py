"""Cloud Storage domain."""

from dataclasses import dataclass
from enum import Enum
from typing import Literal, NewType, Optional

from .organization import OrganizationId
from .project import ProjectId

DataIntegrationId = NewType("DataIntegrationId", str)
DataConnectionId = NewType("DataConnectionId", str)

DataIntegrationPlatform = Literal["AWS", "Azure", "GCP", "CustomS3"]

DataIntegrationStatus = Literal["CONNECTED", "DISCONNECTED", "CHECKING"]


class DataDifferenceType(str, Enum):
    """Data difference type."""

    ADD = "ADD"
    REMOVE = "REMOVE"


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
    """DataConnectionsWhere filters."""

    project_id: Optional[ProjectId]
    integration_id: Optional[DataIntegrationId]
