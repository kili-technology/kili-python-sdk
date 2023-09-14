"""Project domain."""
from dataclasses import dataclass
from typing import Literal, NewType, Optional

from .tag import TagId
from .types import ListOrTuple

ProjectId = NewType("ProjectId", str)
InputType = Literal["IMAGE", "PDF", "TEXT", "VIDEO"]

ComplianceTag = Literal["PHI", "PII"]


@dataclass
# pylint: disable=too-many-instance-attributes
class ProjectFilters:
    """Project filters for running a project search."""

    id: Optional[ProjectId]  # pylint: disable=invalid-name
    archived: Optional[bool] = None
    search_query: Optional[str] = None
    should_relaunch_kpi_computation: Optional[bool] = None
    starred: Optional[bool] = None
    updated_at_gte: Optional[str] = None
    updated_at_lte: Optional[str] = None
    created_at_gte: Optional[str] = None
    created_at_lte: Optional[str] = None
    tag_ids: Optional[ListOrTuple[TagId]] = None
