"""Types for the ProjectWorkflow-related Kili API gateway functions."""

from dataclasses import dataclass
from typing import Optional

from kili.domain.project import WorkflowStepCreate, WorkflowStepUpdate


@dataclass
class ProjectWorkflowDataKiliAPIGatewayInput:
    """ProjectWorkflow input data for Kili API Gateway."""

    enforce_step_separation: Optional[bool]
    create_steps: Optional[list[WorkflowStepCreate]]
    update_steps: Optional[list[WorkflowStepUpdate]]
    delete_steps: Optional[list[str]]
    null_fields: frozenset[str] = frozenset()


@dataclass
class AddReviewStepInput:
    """Input data for adding a review step to a project workflow."""

    project_id: str
    step_name: str
    assignees: list[str]
    step_coverage: int | None = None
    use_honeypot: bool | None = None
    send_back_to_step: str | None = None


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
