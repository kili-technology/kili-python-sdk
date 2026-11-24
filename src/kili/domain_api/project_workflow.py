"""Workflow namespaces of the projects domain, for the Kili Python SDK."""

from typing import TYPE_CHECKING, Any, List, Optional

from typeguard import typechecked

from kili.domain.project import WorkflowStepCreate, WorkflowStepDesignation, WorkflowStepUpdate

if TYPE_CHECKING:
    from kili.client import Kili as KiliLegacy


class WorkflowNamespace:
    """Nested namespace for project workflow operations."""

    def __init__(self, client: "KiliLegacy") -> None:
        """Initialize workflow namespace.

        Args:
            client: The Kili client instance
        """
        self._client = client

    @typechecked
    def update(
        self,
        project_id: str,
        enforce_step_separation: Optional[bool] = None,
        create_steps: Optional[list[WorkflowStepCreate]] = None,
        update_steps: Optional[list[WorkflowStepUpdate]] = None,
        delete_steps: Optional[list[str | WorkflowStepDesignation]] = None,
    ) -> dict[str, Any]:
        """Update properties of a project workflow.

        Args:
            project_id: Id of the project.
            enforce_step_separation: Prevents the same user from being assigned to
                multiple steps in the workflow for a same asset,
                ensuring independent review and labeling processes
            create_steps: List of steps to create in the project workflow. In the multi-group
                workflow, each step gives the `step_group_id` of the group to create it in, and
                consensus can only be set on the labeling step of the first group.
            update_steps: List of steps to update in the project workflow, each given by its `id`,
                or by its `name` with `group_name` when several groups use that name.
            delete_steps: List of steps to delete from the project workflow, each given by its ID,
                by its name, or as `{"name": ..., "group_name": ...}` when several groups use
                that name.

        Returns:
            A dict with the changed properties which indicates if the mutation was successful,
                else an error message.
        """
        return self._client.update_project_workflow(
            project_id=project_id,
            enforce_step_separation=enforce_step_separation,
            create_steps=create_steps,
            update_steps=update_steps,
            delete_steps=delete_steps,
        )

    @typechecked
    def list(self, project_id: str) -> list[dict[str, Any]]:
        """Get steps in a project workflow.

        Args:
            project_id: Id of the project.

        Returns:
            A list with the steps of the project workflow.
        """
        return self._client.get_steps(project_id=project_id)

    @typechecked
    def add_reviewers(
        self,
        project_id: str,
        step_name: Optional[str] = None,
        emails: Optional[List[str]] = None,
        group_name: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> List[str]:
        """Add reviewers to a specific step.

        Args:
            project_id: Id of the project.
            step_name: Name of the step. Exclusive with `step_id`.
            emails: List of emails to add.
            group_name: Name of the group containing the step named `step_name`, in the multi-group
                workflow.
                Required when several groups have a step with the same name.
            step_id: Id of the step. Exclusive with `step_name` and `group_name`.

        Returns:
            A list with emails added to the step.
        """
        return self._client.add_reviewers_to_step(
            project_id=project_id,
            step_name=step_name,
            emails=emails,
            group_name=group_name,
            step_id=step_id,
        )

    @typechecked
    def remove_reviewers(
        self,
        project_id: str,
        step_name: Optional[str] = None,
        emails: Optional[List[str]] = None,
        group_name: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> List[str]:
        """Remove reviewers from a specific step.

        Args:
            project_id: Id of the project.
            step_name: Name of the step. Exclusive with `step_id`.
            emails: List of emails to remove.
            group_name: Name of the group containing the step named `step_name`, in the multi-group
                workflow.
                Required when several groups have a step with the same name.
            step_id: Id of the step. Exclusive with `step_name` and `group_name`.

        Returns:
            A list with emails removed from the step.
        """
        return self._client.remove_reviewers_from_step(
            project_id=project_id,
            step_name=step_name,
            emails=emails,
            group_name=group_name,
            step_id=step_id,
        )

    @typechecked
    def add_labelers(
        self,
        project_id: str,
        step_name: Optional[str] = None,
        emails: Optional[List[str]] = None,
        group_name: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> List[str]:
        """Add labelers to a specific labeling step.

        Only the multi-group workflow supports assigning labelers to a step, and the target step
        must be a labeling step.

        Args:
            project_id: Id of the project.
            step_name: Name of the labeling step. Exclusive with `step_id`.
            emails: List of emails to add.
            group_name: Name of the group containing the step named `step_name`, in the multi-group
                workflow.
                Required when several groups have a step with the same name.
            step_id: Id of the step. Exclusive with `step_name` and `group_name`.

        Returns:
            A list with emails added to the step.
        """
        return self._client.add_labelers_to_step(
            project_id=project_id,
            step_name=step_name,
            emails=emails,
            group_name=group_name,
            step_id=step_id,
        )

    @typechecked
    def remove_labelers(
        self,
        project_id: str,
        step_name: Optional[str] = None,
        emails: Optional[List[str]] = None,
        group_name: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> List[str]:
        """Remove labelers from a specific labeling step.

        Only the multi-group workflow supports removing labelers from a step, and the target step
        must be a labeling step. Removing a labeler also clears their asset-step assignments and
        step queue for that step.

        Args:
            project_id: Id of the project.
            step_name: Name of the labeling step. Exclusive with `step_id`.
            emails: List of emails to remove.
            group_name: Name of the group containing the step named `step_name`, in the multi-group
                workflow.
                Required when several groups have a step with the same name.
            step_id: Id of the step. Exclusive with `step_name` and `group_name`.

        Returns:
            A list with emails removed from the step.
        """
        return self._client.remove_labelers_from_step(
            project_id=project_id,
            step_name=step_name,
            emails=emails,
            group_name=group_name,
            step_id=step_id,
        )

    @typechecked
    def copy_from_project(
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
            >>> kili.projects.workflow.copy_from_project(
            ...     destination_project_id="destination_project_id",
            ...     source_project_id="source_project_id",
            ... )
        """
        return self._client.copy_workflow_from_project(
            destination_project_id=destination_project_id,
            source_project_id=source_project_id,
        )
