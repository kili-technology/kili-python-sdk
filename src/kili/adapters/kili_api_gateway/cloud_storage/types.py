"""Types for the Cloud storage related Kili API gateway functions."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from kili.domain.cloud_storage import DataIntegrationId
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
