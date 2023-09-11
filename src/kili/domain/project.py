"""Project domain."""
from dataclasses import dataclass
from typing import Literal, NewType, Optional

from .tag import TagId
from .types import ListOrTuple

ProjectId = NewType("ProjectId", str)
InputType = Literal[
    "IMAGE",
    "PDF",
    "TEXT",
    "VIDEO",
    "VIDEO_LEGACY",
]


@dataclass
# pylint: disable=too-many-instance-attributes
class ProjectFilters:
    """Project filters for running a project search."""

    id: Optional[ProjectId]  # pylint: disable=invalid-name
    archived: Optional[bool]
    search_query: Optional[str]
    should_relaunch_kpi_computation: Optional[bool]
    starred: Optional[bool]
    updated_at_gte: Optional[str]
    updated_at_lte: Optional[str]
    created_at_gte: Optional[str]
    created_at_lte: Optional[str]
    tag_ids: Optional[ListOrTuple[TagId]]
