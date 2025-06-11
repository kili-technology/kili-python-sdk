"""Project use cases."""

from typing import Dict, List, Optional

from kili.adapters.kili_api_gateway.project_workflow.types import (
    ProjectWorkflowDataKiliAPIGatewayInput,
)
from kili.domain.project import ProjectId, WorkflowStepCreate, WorkflowStepUpdate
from kili.use_cases.base import BaseUseCases


class ProjectWorkflowUseCases(BaseUseCases):
    """ProjectWorkflow use cases."""

    def update_project_workflow(
        self,
        project_id: ProjectId,
        enforce_step_separation: Optional[bool] = None,
        create_steps: Optional[List[WorkflowStepCreate]] = None,
        update_steps: Optional[List[WorkflowStepUpdate]] = None,
        delete_steps: Optional[List[str]] = None,
    ) -> Dict[str, object]:
        """Update properties in a project workflow."""
        project_workflow_data = ProjectWorkflowDataKiliAPIGatewayInput(
            enforce_step_separation=enforce_step_separation,
            create_steps=create_steps,
            update_steps=update_steps,
            delete_steps=delete_steps,
        )

        return self._kili_api_gateway.update_project_workflow(project_id, project_workflow_data)

    def get_steps(
        self,
        project_id: ProjectId,
    ) -> List[Dict[str, object]]:
        """Get steps in a project workflow."""
        return self._kili_api_gateway.get_steps(project_id)
