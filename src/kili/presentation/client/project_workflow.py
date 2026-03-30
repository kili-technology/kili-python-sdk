"""Client presentation methods for project workflow."""

from typing import Any, Optional

from typeguard import typechecked

from kili.domain.project import ProjectId, WorkflowStepCreate, WorkflowStepUpdate
from kili.use_cases.project_workflow import ProjectWorkflowUseCases

from ...domain.types import ListOrTuple
from .base import BaseClientMethods


class ProjectWorkflowClientMethods(BaseClientMethods):
    """Client presentation methods for project workflow."""

    @typechecked
    def update_project_workflow(
        self,
        project_id: str,
        enforce_step_separation: Optional[bool] = None,
        create_steps: Optional[list[WorkflowStepCreate]] = None,
        update_steps: Optional[list[WorkflowStepUpdate]] = None,
        delete_steps: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Update properties of a project workflow.

        Args:
            project_id: Id of the project.
            enforce_step_separation: Prevents the same user from being assigned to
                multiple steps in the workflow for a same asset,
                ensuring independent review and labeling processes
            create_steps: List of steps to create in the project workflow.
            update_steps: List of steps to update in the project workflow.
            delete_steps: List of step IDs or names to delete from the project workflow.

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
        fields: ListOrTuple[str] = (
            "steps.type",
            "steps.name",
            "steps.id",
            "steps.assignees.email",
            "steps.assignees.id",
        ),
    ) -> list[dict[str, Any]]:
        """Get steps in a project workflow.

        Args:
            project_id: Id of the project.
            fields: All the fields to request among the possible fields for the project.
                See the documentation for all possible fields.

        Returns:
            A dict with the steps of the project workflow.
        """
        return ProjectWorkflowUseCases(self.kili_api_gateway).get_steps(
            project_id=ProjectId(project_id), fields=fields
        )

    @typechecked
    def add_reviewers_to_step(
        self, project_id: str, step_name: str, emails: list[str]
    ) -> list[str]:
        """Add reviewers to a specific step.

        Args:
            project_id: Id of the project.
            step_name: Name of the step.
            emails: List of emails to add.

        Returns:
            A list with the added emails.
        """
        return ProjectWorkflowUseCases(self.kili_api_gateway).add_reviewers_to_step(
            project_id=project_id, step_name=step_name, emails=emails
        )

    @typechecked
    def remove_reviewers_from_step(
        self, project_id: str, step_name: str, emails: list[str]
    ) -> list[str]:
        """Remove reviewers from a specific step.

        Args:
            project_id: Id of the project.
            step_name: Name of the step.
            emails: List of emails to remove.

        Returns:
            A list with the removed emails.
        """
        return ProjectWorkflowUseCases(self.kili_api_gateway).remove_reviewers_from_step(
            project_id=project_id, step_name=step_name, emails=emails
        )

    @typechecked
    def copy_workflow_from_project(
        self,
        destination_project_id: str,
        source_project_id: str,
    ) -> dict[str, Any]:
        """Copy the workflow from a source project to a destination project.

        Copies all workflow steps with their configurations (consensus, coverage,
        sendBackStepId) from the source project. Assignees are not copied.

        The destination project must have no labels. Existing workflow steps in the
        destination project will be deleted and replaced by the source workflow.

        Args:
            destination_project_id: Id of the destination project to copy the workflow to.
            source_project_id: Id of the source project to copy the workflow from.

        Returns:
            A dict with the workflow data which indicates if the mutation was successful,
                else an error message.

        Raises:
            ValueError: If the source project has no workflow steps, or if the
                destination project already has labels.

        Examples:
            >>> kili.copy_workflow_from_project(
            ...     destination_project_id="destination_project_id",
            ...     source_project_id="source_project_id",
            ... )
        """
        return ProjectWorkflowUseCases(self.kili_api_gateway).copy_workflow_from_project(
            source_project_id=ProjectId(source_project_id),
            destination_project_id=ProjectId(destination_project_id),
        )
