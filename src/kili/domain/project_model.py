"""API Key domain."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ProjectModelFilters:
    """Project model filters for running a project model search."""

    project_id: Optional[str] = None
    model_id: Optional[str] = None
