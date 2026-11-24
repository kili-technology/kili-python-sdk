"""Project workflow use cases."""

from typing import Optional, cast

from kili.adapters.kili_api_gateway.project_workflow.types import (
    AddReviewStepInput,
    DeleteStepInput,
    ProjectWorkflowDataKiliAPIGatewayInput,
    RenameStepInput,
    UpdateLabelingStepPropertiesInput,
    UpdateReviewStepPropertiesInput,
)
from kili.domain.project import (
    ProjectId,
    WorkflowStepCreate,
    WorkflowStepDesignation,
    WorkflowStepUpdate,
)
from kili.domain.types import ListOrTuple
from kili.use_cases.base import BaseUseCases
from kili.use_cases.project_workflow.copy_workflow import WorkflowCopyUseCases


class ProjectWorkflowUseCases(BaseUseCases):
    """ProjectWorkflow use cases."""

    def update_project_workflow(
        self,
        project_id: ProjectId,
        enforce_step_separation: Optional[bool] = None,
        create_steps: Optional[list[WorkflowStepCreate]] = None,
        update_steps: Optional[list[WorkflowStepUpdate]] = None,
        delete_steps: Optional[list[str | WorkflowStepDesignation]] = None,
    ) -> dict[str, object]:
        """Update properties in a project workflow.

        A step to update or delete is sent by id: one given by name, with its group when several
        groups use that name, is resolved to its id first.
        """
        project_workflow_data = ProjectWorkflowDataKiliAPIGatewayInput(
            enforce_step_separation=enforce_step_separation,
            create_steps=create_steps,
            update_steps=self._update_steps_by_id(project_id, update_steps),
            delete_steps=self._delete_steps_by_id(project_id, delete_steps),
        )

        return self._kili_api_gateway.update_project_workflow(project_id, project_workflow_data)

    def _update_steps_by_id(
        self, project_id: ProjectId, update_steps: Optional[list[WorkflowStepUpdate]]
    ) -> Optional[list[WorkflowStepUpdate]]:
        """The updates, each naming its step by id.

        With an `id`, `name` is the new name of the step; without one, `name` (and `group_name`)
        says which step it is.
        """
        if not update_steps:
            return update_steps

        steps_by_id: list[WorkflowStepUpdate] = []
        for update in update_steps:
            update = cast(WorkflowStepUpdate, dict(update))
            group_name = update.pop("group_name", None)
            if update.get("id") is None:
                step_name = update.get("name")
                if step_name is None:
                    raise ValueError("A step to update is given by its id, or by its name")
                update["id"] = self._kili_api_gateway.get_step(
                    project_id, step_name=step_name, group_name=group_name
                )["id"]
            elif group_name is not None:
                raise ValueError(
                    "group_name goes with a step given by its name, not with one given by its id"
                )
            steps_by_id.append(update)
        return steps_by_id

    def _delete_steps_by_id(
        self,
        project_id: ProjectId,
        delete_steps: Optional[list[str | WorkflowStepDesignation]],
    ) -> Optional[list[str]]:
        """The ids of the steps to delete, each given by id, by name, or by name and group."""
        if not delete_steps:
            return cast(Optional[list[str]], delete_steps)

        context = self._kili_api_gateway.get_project_workflow_context(project_id)
        step_ids = {step["id"] for step in context.get("steps") or []}
        resolved: list[str] = []
        for step in delete_steps:
            if isinstance(step, str) and step in step_ids:
                resolved.append(step)
                continue
            name, group_name = (
                (step, None) if isinstance(step, str) else (step["name"], step.get("group_name"))
            )
            resolved.append(
                self._kili_api_gateway.get_step(project_id, step_name=name, group_name=group_name)[
                    "id"
                ]
            )
        # A step given twice, by id and by name, is deleted once.
        return list(dict.fromkeys(resolved))

    def get_steps(
        self,
        project_id: ProjectId,
        fields: ListOrTuple[str],
    ) -> list[dict[str, object]]:
        """Get steps in a project workflow."""
        return self._kili_api_gateway.get_steps(project_id, fields)

    def add_reviewers_to_step(
        self,
        project_id: str,
        step_name: Optional[str],
        emails: list[str],
        group_name: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> list[str]:
        """Add reviewers to a specific step."""
        return self._kili_api_gateway.add_reviewers_to_step(
            project_id, step_name, emails, group_name, step_id
        )

    def remove_reviewers_from_step(
        self,
        project_id: str,
        step_name: Optional[str],
        emails: list[str],
        group_name: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> list[str]:
        """Remove reviewers from a specific step."""
        return self._kili_api_gateway.remove_reviewers_from_step(
            project_id, step_name, emails, group_name, step_id
        )

    def add_labelers_to_step(
        self,
        project_id: str,
        step_name: Optional[str],
        emails: list[str],
        group_name: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> list[str]:
        """Add labelers to a specific step."""
        return self._kili_api_gateway.add_labelers_to_step(
            project_id, step_name, emails, group_name, step_id
        )

    def remove_labelers_from_step(
        self,
        project_id: str,
        step_name: Optional[str],
        emails: list[str],
        group_name: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> list[str]:
        """Remove labelers from a specific step."""
        return self._kili_api_gateway.remove_labelers_from_step(
            project_id, step_name, emails, group_name, step_id
        )

    def copy_workflow_from_project(
        self,
        source_project_id: ProjectId,
        destination_project_id: ProjectId,
    ) -> dict[str, object]:
        """Copy a workflow from one project to another."""
        return WorkflowCopyUseCases(self._kili_api_gateway).copy_workflow_from_project(
            source_project_id=source_project_id,
            destination_project_id=destination_project_id,
        )

    def add_review_step(
        self,
        project_id: str,
        step_name: str,
        assignees: list[str],
        step_coverage: int | None = None,
        use_honeypot: bool | None = None,
        send_back_to_step: str | None = None,
        group_name: str | None = None,
    ) -> dict[str, object]:
        """Add a review step to a project workflow."""
        if step_coverage and not 0 <= step_coverage <= 100:
            raise ValueError("The parameter step_coverage must be between 0 and 100 (included).")
        data = AddReviewStepInput(
            project_id=project_id,
            step_name=step_name,
            assignees=assignees,
            step_coverage=step_coverage,
            use_honeypot=use_honeypot,
            send_back_to_step=send_back_to_step,
            group_name=group_name,
        )
        return self._kili_api_gateway.add_review_step(data)

    def update_labeling_step_properties(
        self,
        project_id: str,
        step_name: str | None = None,
        consensus_coverage: int | None = None,
        number_of_expected_labels_for_consensus: int | None = None,
        use_honeypot: bool | None = None,
        group_name: str | None = None,
        step_id: str | None = None,
    ) -> dict[str, object]:
        """Update properties of a labeling step."""
        if consensus_coverage and not 0 <= consensus_coverage <= 100:
            raise ValueError(
                "The parameter consensus_coverage must be between 0 and 100 (included)."
            )
        step_id = self._kili_api_gateway.get_step(
            project_id, step_id=step_id, step_name=step_name, group_name=group_name
        )["id"]
        data = UpdateLabelingStepPropertiesInput(
            project_id=project_id,
            step_id=str(step_id),
            consensus_coverage=consensus_coverage,
            number_of_expected_labels_for_consensus=number_of_expected_labels_for_consensus,
            use_honeypot=use_honeypot,
        )
        return self._kili_api_gateway.update_labeling_step_properties(data)

    def update_review_step_properties(
        self,
        project_id: str,
        step_name: str | None = None,
        assignees: list[str] | None = None,
        step_coverage: int | None = None,
        send_back_to_step: str | None = None,
        use_honeypot: bool | None = None,
        group_name: str | None = None,
        step_id: str | None = None,
    ) -> dict[str, object]:
        """Update properties of a review step."""
        if step_coverage and not 0 <= step_coverage <= 100:
            raise ValueError("The parameter step_coverage must be between 0 and 100 (included).")
        step_id = self._kili_api_gateway.get_step(
            project_id, step_id=step_id, step_name=step_name, group_name=group_name
        )["id"]
        data = UpdateReviewStepPropertiesInput(
            project_id=project_id,
            step_id=str(step_id),
            assignees=assignees,
            step_coverage=step_coverage,
            send_back_to_step=send_back_to_step,
            use_honeypot=use_honeypot,
        )
        return self._kili_api_gateway.update_review_step_properties(data)

    def delete_last_step(
        self,
        project_id: str,
    ) -> dict[str, object]:
        """Delete the last review step from a project workflow."""
        steps = self._kili_api_gateway.get_steps(
            project_id=ProjectId(project_id), fields=["steps.id", "steps.name"]
        )
        if len(steps) <= 2:
            raise ValueError(
                "Cannot delete the last review step if only one review step is remaining."
            )
        step = steps[-1]
        data = DeleteStepInput(project_id=project_id, step_id=str(step["id"]))
        return self._kili_api_gateway.delete_step(data)

    def rename_step(
        self,
        project_id: str,
        new_name: str,
        step_name: str | None = None,
        group_name: str | None = None,
        step_id: str | None = None,
    ) -> dict[str, object]:
        """Rename a step in a project workflow."""
        step_id = self._kili_api_gateway.get_step(
            project_id, step_id=step_id, step_name=step_name, group_name=group_name
        )["id"]
        data = RenameStepInput(project_id=project_id, step_id=str(step_id), new_name=new_name)
        return self._kili_api_gateway.rename_step(data)
