"""Types for the ProjectWorkflow-related Kili API gateway functions."""

from dataclasses import dataclass
from typing import List, Optional

from kili.domain.project import WorkflowStepCreate, WorkflowStepUpdate


@dataclass
class ProjectWorkflowDataKiliAPIGatewayInput:
    """ProjectWorkflow input data for Kili API Gateway."""

    enforce_step_separation: Optional[bool]
    create_steps: Optional[List[WorkflowStepCreate]]
    update_steps: Optional[List[WorkflowStepUpdate]]
    delete_steps: Optional[List[str]]
