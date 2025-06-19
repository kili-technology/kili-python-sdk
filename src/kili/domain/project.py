"""Project domain."""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, List, Literal, NewType, Optional, TypedDict

from typing_extensions import Required

from .types import ListOrTuple

if TYPE_CHECKING:
    from .tag import TagId

ProjectId = NewType("ProjectId", str)
InputType = Literal[
    "IMAGE", "GEOSPATIAL", "PDF", "TEXT", "VIDEO", "LLM_RLHF", "LLM_INSTR_FOLLOWING", "LLM_STATIC"
]


@dataclass(frozen=True)
class ProjectStep(TypedDict, total=True):
    """Project step type."""

    id: str
    name: str


class WorkflowStepCreate(TypedDict, total=False):
    """Project workflow step."""

    name: Required[str]
    consensus_coverage: Optional[int]
    number_of_expected_labels_for_consensus: Optional[int]
    order: Required[int]
    step_coverage: Optional[int]
    type: Required[Literal["DEFAULT", "REVIEW"]]
    assignees: Required[List[str]]


class WorkflowStepUpdate(TypedDict, total=False):
    """Project workflow step."""

    id: Required[str]
    name: Optional[str]
    consensus_coverage: Optional[int]
    number_of_expected_labels_for_consensus: Optional[int]
    order: Optional[int]
    step_coverage: Optional[int]
    type: Optional[Literal["DEFAULT", "REVIEW"]]
    assignees: Optional[List[str]]


class InputTypeEnum(str, Enum):
    """Input type enum."""

    IMAGE = "IMAGE"
    PDF = "PDF"
    TEXT = "TEXT"
    VIDEO = "VIDEO"
    LLM_RLHF = "LLM_RLHF"
    LLM_INSTR_FOLLOWING = "LLM_INSTR_FOLLOWING"
    LLM_STATIC = "LLM_STATIC"


ComplianceTag = Literal["PHI", "PII"]


@dataclass
# pylint: disable=too-many-instance-attributes
class ProjectFilters:
    """Project filters for running a project search."""

    id: Optional[ProjectId]
    archived: Optional[bool] = None
    search_query: Optional[str] = None
    should_relaunch_kpi_computation: Optional[bool] = None
    starred: Optional[bool] = None
    updated_at_gte: Optional[str] = None
    updated_at_lte: Optional[str] = None
    created_at_gte: Optional[str] = None
    created_at_lte: Optional[str] = None
    organization_id: Optional[str] = None
    tag_ids: Optional[ListOrTuple["TagId"]] = None
    deleted: Optional[bool] = None
