"""Project domain."""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Literal, NewType, Optional, TypedDict, Union

from typing_extensions import Required

from .types import ListOrTuple

if TYPE_CHECKING:
    from .tag import TagId

ProjectId = NewType("ProjectId", str)
InputType = Literal[
    "IMAGE",
    "GEOSPATIAL",
    "PDF",
    "TEXT",
    "VIDEO",
    "LLM_RLHF",
    "LLM_INSTR_FOLLOWING",
    "LLM_STATIC",
    "AUDIO",
]
WorkflowVersion = Literal["V1", "V2", "V3"]


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
    step_coverage: Optional[int]
    type: Required[Literal["DEFAULT", "REVIEW"]]
    assignees: Required[list[str]]
    send_back_step_id: Optional[str]
    # The group to create the step in, required on multi-group workflow projects.
    step_group_id: Optional[str]


class WorkflowStepDesignation(TypedDict, total=False):
    """A step given by its name, with its group when several groups use that name."""

    name: Required[str]
    group_name: Optional[str]


class WorkflowStepUpdate(TypedDict, total=False):
    """Project workflow step."""

    id: Optional[str]
    name: Optional[str]
    consensus_coverage: Optional[int]
    number_of_expected_labels_for_consensus: Optional[int]
    step_coverage: Optional[int]
    type: Optional[Literal["DEFAULT", "REVIEW"]]
    assignees: Optional[list[str]]
    send_back_step_id: Optional[str]
    # With no `id`, the step is found by `name`, which is unique per group only: the group name
    # says which group's step it is when several groups use that name.
    group_name: Optional[str]


class WorkflowStepToCreate(WorkflowStepCreate, total=False):
    """A step to create, with the id to give it.

    The id, unique across Kili and 5 to 32 characters long, is chosen by the caller, so that the
    other changes of the same call can name the step: a step created after it sends back to it with
    `send_back_step_id`.
    """

    id: Optional[str]


class WorkflowStepToUpdate(WorkflowStepUpdate, total=False):
    """A step to update, honeypot and send back to the previous step included."""

    use_honeypot: Optional[bool]
    send_back_to_previous_step: Optional[bool]


class WorkflowStepGroupToCreate(TypedDict, total=False):
    """A step group to create, with its steps, in the multi-group workflow.

    Its steps are its labeling step first, then at least one review. The id, unique across Kili and
    5 to 32 characters long, is chosen by the caller, so that a step created in the same call can
    name the group by it in `step_group_id`.
    """

    id: Optional[str]
    name: Required[str]
    allowed_job_names: Optional[list[str]]
    steps: Required[list[WorkflowStepToCreate]]


class WorkflowStepGroupToUpdate(TypedDict, total=False):
    """A step group to update, given by its id, in the multi-group workflow."""

    id: Required[str]
    name: Optional[str]
    allowed_job_names: Optional[list[str]]


class WorkflowTransitionCondition(TypedDict, total=False):
    """What must hold for an asset to take a transition.

    `type` is one of `ALWAYS`, `SAMPLE` (with its `percentage`), `CLASSIFICATION_INCLUDES` (with
    its `job_name`, `categories`, and optionally a `quantifier`: `ANY`, `EVERY` or `MORE_THAN`
    with a `value`) or `ANNOTATION_COUNT_GREATER_THAN` (with its `value`, and optionally a
    `job_name`). Kili may add others.
    """

    type: Required[str]
    percentage: Optional[int]
    job_name: Optional[str]
    categories: Optional[list[str]]
    quantifier: Optional[str]
    value: Optional[int]


class WorkflowTransitionToCreate(TypedDict, total=False):
    """A transition to create, from a step (`from_step`) or a group's end (`from_step_group`).

    A step is given by its id, by its name, as `{"name": ..., "group_name": ...}`, or by the id
    given to a step created in the same call; a group by its id or its name, or by the id given to
    a group created in the same call. Without `to_step`, the asset leaves the workflow.
    """

    from_step: Union[str, WorkflowStepDesignation]
    from_step_group: str
    to_step: Optional[Union[str, WorkflowStepDesignation]]
    priority: Required[int]
    condition: Required[WorkflowTransitionCondition]


class WorkflowTransitionToUpdate(TypedDict, total=False):
    """A stored transition to change, given by its id: its priority and its condition.

    A transition keeps its source and target: given, `from_step`, `from_step_group` and `to_step`
    must name the ones it has. To change them, delete it and create another.
    """

    id: Required[str]
    priority: Optional[int]
    condition: Optional[WorkflowTransitionCondition]
    from_step: Union[str, WorkflowStepDesignation]
    from_step_group: str
    to_step: Optional[Union[str, WorkflowStepDesignation]]


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
