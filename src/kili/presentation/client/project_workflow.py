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
        self,
        project_id: str,
        step_name: str,
        emails: list[str],
        group_name: Optional[str] = None,
    ) -> list[str]:
        """Add reviewers to a specific step.

        Args:
            project_id: Id of the project.
            step_name: Name of the step.
            emails: List of emails to add.
            group_name: Name of the workflow V3 group containing the step.
                Required when several groups have a step with the same name.

        Returns:
            A list with the added emails.
        """
        return ProjectWorkflowUseCases(self.kili_api_gateway).add_reviewers_to_step(
            project_id=project_id, step_name=step_name, emails=emails, group_name=group_name
        )

    @typechecked
    def remove_reviewers_from_step(
        self,
        project_id: str,
        step_name: str,
        emails: list[str],
        group_name: Optional[str] = None,
    ) -> list[str]:
        """Remove reviewers from a specific step.

        Args:
            project_id: Id of the project.
            step_name: Name of the step.
            emails: List of emails to remove.
            group_name: Name of the workflow V3 group containing the step.
                Required when several groups have a step with the same name.

        Returns:
            A list with the removed emails.
        """
        return ProjectWorkflowUseCases(self.kili_api_gateway).remove_reviewers_from_step(
            project_id=project_id, step_name=step_name, emails=emails, group_name=group_name
        )

    @typechecked
    def add_labelers_to_step(
        self,
        project_id: str,
        step_name: str,
        emails: list[str],
        group_name: Optional[str] = None,
    ) -> list[str]:
        """Add labelers to a specific labeling step.

        Only workflow V3 projects support assigning labelers to a step, and the target step must
        be a labeling step.

        Args:
            project_id: Id of the project.
            step_name: Name of the labeling step.
            emails: List of emails to add.
            group_name: Name of the workflow V3 group containing the step.
                Required when several groups have a step with the same name.

        Returns:
            A list with the added emails.
        """
        return ProjectWorkflowUseCases(self.kili_api_gateway).add_labelers_to_step(
            project_id=project_id, step_name=step_name, emails=emails, group_name=group_name
        )

    @typechecked
    def remove_labelers_from_step(
        self,
        project_id: str,
        step_name: str,
        emails: list[str],
        group_name: Optional[str] = None,
    ) -> list[str]:
        """Remove labelers from a specific labeling step.

        Only workflow V3 projects support removing labelers from a step, and the target step must
        be a labeling step. Removing a labeler also clears their asset-step assignments and step
        queue for that step.

        Args:
            project_id: Id of the project.
            step_name: Name of the labeling step.
            emails: List of emails to remove.
            group_name: Name of the workflow V3 group containing the step.
                Required when several groups have a step with the same name.

        Returns:
            A list with the removed emails.
        """
        return ProjectWorkflowUseCases(self.kili_api_gateway).remove_labelers_from_step(
            project_id=project_id, step_name=step_name, emails=emails, group_name=group_name
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

    @typechecked
    def add_review_step(
        self,
        project_id: str,
        step_name: str,
        assignees: list[str],
        step_coverage: int | None = None,
        use_honeypot: bool | None = None,
        send_back_to_step: str | None = None,
    ) -> dict[str, Any]:
        """Add a review step to a project workflow.

        Args:
            project_id: Id of the project.
            step_name: Name of the new review step.
            assignees: List of user emails to assign as reviewers.
            step_coverage: Percentage of assets to be reviewed in this step (0-100).
            use_honeypot: Whether to use honeypot on this step.
            send_back_to_step: Name of the step to send assets back to.

        Returns:
            A dict with the created step data (id, name).
        """
        return ProjectWorkflowUseCases(self.kili_api_gateway).add_review_step(
            project_id=project_id,
            step_name=step_name,
            assignees=assignees,
            step_coverage=step_coverage,
            use_honeypot=use_honeypot,
            send_back_to_step=send_back_to_step,
        )

    @typechecked
    def update_labeling_step_properties(
        self,
        project_id: str,
        step_name: str,
        consensus_coverage: int | None = None,
        number_of_expected_labels_for_consensus: int | None = None,
        use_honeypot: bool | None = None,
    ) -> dict[str, Any]:
        """Update properties of a labeling step.

        Args:
            project_id: Id of the project.
            step_name: Name of the labeling step to update.
            consensus_coverage: Percentage of assets to be labeled for consensus (0-100).
            number_of_expected_labels_for_consensus: Number of expected labels for consensus.
            use_honeypot: Whether to use honeypot on this step.

        Returns:
            A dict with the updated step data (id, name).
        """
        return ProjectWorkflowUseCases(self.kili_api_gateway).update_labeling_step_properties(
            project_id=project_id,
            step_name=step_name,
            consensus_coverage=consensus_coverage,
            number_of_expected_labels_for_consensus=number_of_expected_labels_for_consensus,
            use_honeypot=use_honeypot,
        )

    @typechecked
    def update_review_step_properties(
        self,
        project_id: str,
        step_name: str,
        assignees: list[str] | None = None,
        step_coverage: int | None = None,
        send_back_to_step: str | None = None,
        use_honeypot: bool | None = None,
    ) -> dict[str, Any]:
        """Update properties of a review step.

        Args:
            project_id: Id of the project.
            step_name: Name of the review step to update.
            assignees: List of emails to assign to the step.
            step_coverage: Percentage of assets to be reviewed in this step (0-100).
            send_back_to_step: Id of the step to send assets back to when rejected.
            use_honeypot: Whether to use honeypot on this step.

        Returns:
            A dict with the updated step data (id, name).
        """
        return ProjectWorkflowUseCases(self.kili_api_gateway).update_review_step_properties(
            project_id=project_id,
            step_name=step_name,
            assignees=assignees,
            step_coverage=step_coverage,
            send_back_to_step=send_back_to_step,
            use_honeypot=use_honeypot,
        )

    @typechecked
    def delete_last_step(
        self,
        project_id: str,
    ) -> dict[str, Any]:
        """Delete the last review step from a project workflow.

        Args:
            project_id: Id of the project.

        Returns:
            A dict with the remaining steps.
        """
        return ProjectWorkflowUseCases(self.kili_api_gateway).delete_last_step(
            project_id=project_id,
        )

    @typechecked
    def rename_step(
        self,
        project_id: str,
        step_name: str,
        new_name: str,
    ) -> dict[str, Any]:
        """Rename a step in a project workflow.

        Args:
            project_id: Id of the project.
            step_name: Name of the step.
            new_name: New name for the step.

        Returns:
            A dict with the renamed step data (id, name).
        """
        return ProjectWorkflowUseCases(self.kili_api_gateway).rename_step(
            project_id=project_id,
            step_name=step_name,
            new_name=new_name,
        )
