"""Client presentation methods for project workflow."""

from typing import Any, Dict, List, Optional

from typeguard import typechecked

from kili.domain.project import ProjectId, WorkflowStepCreate, WorkflowStepUpdate
from kili.use_cases.project_workflow import ProjectWorkflowUseCases

from .base import BaseClientMethods


class ProjectWorkflowClientMethods(BaseClientMethods):
    """Client presentation methods for project workflow."""

    @typechecked
    def update_project_workflow(
        self,
        project_id: str,
        enforce_step_separation: Optional[bool] = None,
        create_steps: Optional[List[WorkflowStepCreate]] = None,
        update_steps: Optional[List[WorkflowStepUpdate]] = None,
        delete_steps: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Update properties of a project workflow.

        Args:
            project_id: Id of the project.
            enforce_step_separation: Prevents the same user from being assigned to
                multiple steps in the workflow for a same asset,
                ensuring independent review and labeling processes
            create_steps: List of steps to create in the project workflow.
            update_steps: List of steps to update in the project workflow.
            delete_steps: List of step IDs to delete from the project workflow.

        Returns:
            A dict with the changed properties which indicates if the mutation was successful,
                else an error message.
        """
        return ProjectWorkflowUseCases(self.kili_api_gateway).update_project_workflow(
            project_id=ProjectId(project_id),
            enforce_step_separation=enforce_step_separation,
            create_steps=create_steps,
            update_steps=update_steps,
            delete_steps=delete_steps,
        )

    @typechecked
    def get_steps(
        self,
        project_id: str,
    ) -> List[Dict[str, Any]]:
        """Get steps in a project workflow.

        Args:
            project_id: Id of the project.

        Returns:
            A dict with the steps of the project workflow.
        """
        return ProjectWorkflowUseCases(self.kili_api_gateway).get_steps(
            project_id=ProjectId(project_id),
        )
