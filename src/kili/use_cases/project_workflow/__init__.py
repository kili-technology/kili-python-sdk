"""Project use cases."""

from typing import Dict, Optional

from kili.adapters.kili_api_gateway.project_workflow.types import (
    ProjectWorkflowDataKiliAPIGatewayInput,
)
from kili.domain.project import ProjectId
from kili.use_cases.base import BaseUseCases


class ProjectWorkflowUseCases(BaseUseCases):
    """ProjectWorkflow use cases."""

    def update_project_workflow(
        self,
        project_id: ProjectId,
        enforce_step_separation: Optional[bool] = None,
    ) -> Dict[str, object]:
        """Update properties in a project workflow."""
        project_workflow_data = ProjectWorkflowDataKiliAPIGatewayInput(
            enforce_step_separation=enforce_step_separation,
        )

        return self._kili_api_gateway.update_project_workflow(project_id, project_workflow_data)
