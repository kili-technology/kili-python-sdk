"""Types for the ProjectWorkflow-related Kili API gateway functions."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Optional

from kili.domain.project import (
    WorkflowStepCreate,
    WorkflowStepGroupToCreate,
    WorkflowStepGroupToUpdate,
    WorkflowStepUpdate,
)


@dataclass
class ProjectWorkflowDataKiliAPIGatewayInput:
    """ProjectWorkflow input data for Kili API Gateway."""

    enforce_step_separation: Optional[bool]
    create_steps: Optional[Sequence[WorkflowStepCreate]]
    update_steps: Optional[list[WorkflowStepUpdate]]
    # Step ids only: names are resolved to ids before the request is built.
    delete_steps: Optional[list[str]]
    null_fields: frozenset[str] = frozenset()
    create_step_groups: Optional[list[WorkflowStepGroupToCreate]] = None
    update_step_groups: Optional[list[WorkflowStepGroupToUpdate]] = None
    # Group ids only, as the steps to delete.
    delete_step_groups: Optional[list[str]] = None
    # Every transition of the workflow, as the API takes them: those not listed are removed.
    transitions: Optional[list[dict]] = None


@dataclass
class AddReviewStepInput:
    """Input data for adding a review step to a project workflow."""

    project_id: str
    step_name: str
    assignees: list[str]
    step_coverage: int | None = None
    use_honeypot: bool | None = None
    send_back_to_step: str | None = None
    # The group to add the step to, by name; resolved to its id before the request is built.
    group_name: str | None = None
    step_group_id: str | None = None
    send_back_to_previous_step: bool | None = None


@dataclass
class UpdateLabelingStepPropertiesInput:
    """Input data for updating labeling step properties."""

    project_id: str
    step_id: str
    consensus_coverage: int | None = None
    number_of_expected_labels_for_consensus: int | None = None
    use_honeypot: bool | None = None


@dataclass
class UpdateReviewStepPropertiesInput:
    """Input data for updating review step properties."""

    project_id: str
    step_id: str
    assignees: list[str] | None = None
    step_coverage: int | None = None
    send_back_to_step: str | None = None
    use_honeypot: bool | None = None


@dataclass
class DeleteStepInput:
    """Input data for deleting a step from a project workflow."""

    project_id: str
    step_id: str


@dataclass
class RenameStepInput:
    """Input data for renaming a step in a project workflow."""

    project_id: str
    step_id: str
    new_name: str
