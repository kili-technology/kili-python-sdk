"""Types for the ProjectWorkflow-related Kili API gateway functions."""

from dataclasses import dataclass

from kili.domain.project import WorkflowStepCreate, WorkflowStepUpdate


@dataclass
class ProjectWorkflowDataKiliAPIGatewayInput:
    """ProjectWorkflow input data for Kili API Gateway."""

    enforce_step_separation: bool | None
    create_steps: list[WorkflowStepCreate] | None
    update_steps: list[WorkflowStepUpdate] | None
    delete_steps: list[str] | None


@dataclass
class AddReviewStepInput:
    """Input data for adding a review step to a project workflow."""

    project_id: str
    name: str
    assignees: list[str]
    consensus_coverage: int | None = None
    number_of_expected_labels_for_consensus: int | None = None
    step_coverage: int | None = None
    use_honeypot: bool | None = None
    send_back_to_step: str | None = None


@dataclass
class UpdateLabelingStepPropertiesInput:
    """Input data for updating labeling step properties."""

    project_id: str
    step_name: str
    consensus_coverage: int | None = None
    number_of_expected_labels_for_consensus: int | None = None
    use_honeypot: bool | None = None


@dataclass
class UpdateReviewStepPropertiesInput:
    """Input data for updating review step properties."""

    project_id: str
    step_name: str
    step_coverage: int | None = None
    send_back_to_step: str | None = None
    use_honeypot: bool | None = None


@dataclass
class DeleteStepInput:
    """Input data for deleting a step from a project workflow."""

    project_id: str
    step_name: str


@dataclass
class RenameStepInput:
    """Input data for renaming a step in a project workflow."""

    project_id: str
    step_name: str
    new_name: str
