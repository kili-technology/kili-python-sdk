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
