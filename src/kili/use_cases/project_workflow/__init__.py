"""Project use cases."""

import logging

from kili.adapters.kili_api_gateway.project_workflow.types import (
    AddReviewStepInput,
    DeleteStepInput,
    ProjectWorkflowDataKiliAPIGatewayInput,
    RenameStepInput,
    UpdateLabelingStepPropertiesInput,
    UpdateReviewStepPropertiesInput,
)
from kili.domain.label import LabelFilters
from kili.domain.project import ProjectId, WorkflowStepCreate, WorkflowStepUpdate
from kili.domain.types import ListOrTuple
from kili.use_cases.base import BaseUseCases

logger = logging.getLogger(__name__)

_SOURCE_STEP_FIELDS = (
    "steps.id",
    "steps.name",
    "steps.type",
    "steps.consensusCoverage",
    "steps.numberOfExpectedLabelsForConsensus",
    "steps.stepCoverage",
    "steps.sendBackStepId",
)


class ProjectWorkflowUseCases(BaseUseCases):
    """ProjectWorkflow use cases."""

    def update_project_workflow(
        self,
        project_id: ProjectId,
        enforce_step_separation: bool | None = None,
        create_steps: list[WorkflowStepCreate] | None = None,
        update_steps: list[WorkflowStepUpdate] | None = None,
        delete_steps: list[str] | None = None,
    ) -> dict[str, object]:
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
        fields: ListOrTuple[str],
    ) -> list[dict[str, object]]:
        """Get steps in a project workflow."""
        return self._kili_api_gateway.get_steps(project_id, fields)

    def add_reviewers_to_step(
        self, project_id: str, step_name: str, emails: list[str]
    ) -> list[str]:
        """Add reviewers to a specific step."""
        return self._kili_api_gateway.add_reviewers_to_step(project_id, step_name, emails)

    def remove_reviewers_from_step(
        self, project_id: str, step_name: str, emails: list[str]
    ) -> list[str]:
        """Remove reviewers from a specific step."""
        return self._kili_api_gateway.remove_reviewers_from_step(project_id, step_name, emails)

    def add_review_step(
        self,
        project_id: str,
        name: str,
        assignees: list[str],
        consensus_coverage: int | None = None,
        number_of_expected_labels_for_consensus: int | None = None,
        step_coverage: int | None = None,
        use_honeypot: bool | None = None,
        send_back_to_step: str | None = None,
    ) -> dict[str, object]:
        """Add a review step to a project workflow."""
        data = AddReviewStepInput(
            project_id=project_id,
            name=name,
            assignees=assignees,
            consensus_coverage=consensus_coverage,
            number_of_expected_labels_for_consensus=number_of_expected_labels_for_consensus,
            step_coverage=step_coverage,
            use_honeypot=use_honeypot,
            send_back_to_step=send_back_to_step,
        )
        return self._kili_api_gateway.add_review_step(data)

    def update_labeling_step_properties(
        self,
        project_id: str,
        step_name: str,
        consensus_coverage: int | None = None,
        number_of_expected_labels_for_consensus: int | None = None,
        use_honeypot: bool | None = None,
    ) -> dict[str, object]:
        """Update properties of a labeling step."""
        data = UpdateLabelingStepPropertiesInput(
            project_id=project_id,
            step_name=step_name,
            consensus_coverage=consensus_coverage,
            number_of_expected_labels_for_consensus=number_of_expected_labels_for_consensus,
            use_honeypot=use_honeypot,
        )
        return self._kili_api_gateway.update_labeling_step_properties(data)

    def update_review_step_properties(
        self,
        project_id: str,
        step_name: str,
        step_coverage: int | None = None,
        send_back_to_step: str | None = None,
        use_honeypot: bool | None = None,
    ) -> dict[str, object]:
        """Update properties of a review step."""
        data = UpdateReviewStepPropertiesInput(
            project_id=project_id,
            step_name=step_name,
            step_coverage=step_coverage,
            send_back_to_step=send_back_to_step,
            use_honeypot=use_honeypot,
        )
        return self._kili_api_gateway.update_review_step_properties(data)

    def delete_step(
        self,
        project_id: str,
        step_name: str,
    ) -> dict[str, object]:
        """Delete a step from a project workflow."""
        data = DeleteStepInput(
            project_id=project_id,
            step_name=step_name,
        )
        return self._kili_api_gateway.delete_step(data)

    def rename_step(
        self,
        project_id: str,
        step_name: str,
        new_name: str,
    ) -> dict[str, object]:
        """Rename a step in a project workflow."""
        data = RenameStepInput(
            project_id=project_id,
            step_name=step_name,
            new_name=new_name,
        )
        return self._kili_api_gateway.rename_step(data)

    def copy_workflow_from_project(
        self,
        source_project_id: ProjectId,
        destination_project_id: ProjectId,
    ) -> dict[str, object]:
        """Copy a workflow from one project to another.

        Fetches the source workflow steps, validates the destination project has no labels,
        deletes existing destination steps, and creates new steps with remapped sendBackStepId
        references.
        """
        # 1. Fetch source workflow steps
        logger.info("Fetching workflow steps from source project %s", source_project_id)
        source_steps = self._kili_api_gateway.get_steps(source_project_id, _SOURCE_STEP_FIELDS)

        if not source_steps:
            raise ValueError(f"Source project {source_project_id} has no workflow steps to copy.")

        # 2. Validate destination has no labels
        logger.info(
            "Validating destination project %s has no labels",
            destination_project_id,
        )
        label_count = self._kili_api_gateway.count_labels(
            filters=LabelFilters(project_id=destination_project_id)
        )
        if label_count > 0:
            raise ValueError(
                f"Destination project {destination_project_id} already has"
                f" {label_count} label(s). Cannot copy workflow to a project"
                " that has already been labeled."
            )

        # 3. Delete existing destination steps
        logger.info(
            "Fetching existing steps from destination project %s",
            destination_project_id,
        )
        try:
            dest_steps = self._kili_api_gateway.get_steps(
                destination_project_id, ("steps.id", "steps.name")
            )
        except Exception:
            dest_steps = []

        dest_step_ids = [step["id"] for step in dest_steps]

        # 4. Build create steps
        steps_to_create: list[WorkflowStepCreate] = []
        source_steps_with_send_back: list[tuple[int, str]] = []

        for idx, step in enumerate(source_steps):
            create_step: WorkflowStepCreate = {
                "name": step["name"],
                "type": step["type"],
                "assignees": [],  # Don't copy assignees per spec
            }
            if step.get("consensusCoverage") is not None:
                create_step["consensus_coverage"] = step["consensusCoverage"]
            if step.get("numberOfExpectedLabelsForConsensus") is not None:
                create_step["number_of_expected_labels_for_consensus"] = step[
                    "numberOfExpectedLabelsForConsensus"
                ]
            if step.get("stepCoverage") is not None:
                create_step["step_coverage"] = step["stepCoverage"]

            # Track steps that have sendBackStepId for remapping later
            if step.get("sendBackStepId"):
                source_steps_with_send_back.append((idx, step["sendBackStepId"]))

            steps_to_create.append(create_step)

        # 5. Execute: delete existing + create new steps in a single call
        logger.info(
            "Copying %d steps from project %s to project %s",
            len(steps_to_create),
            source_project_id,
            destination_project_id,
        )

        result = self._kili_api_gateway.update_project_workflow(
            destination_project_id,
            ProjectWorkflowDataKiliAPIGatewayInput(
                enforce_step_separation=None,
                create_steps=steps_to_create,
                update_steps=None,
                delete_steps=dest_step_ids if dest_step_ids else None,
            ),
        )

        # 6. Remap sendBackStepId references if any steps had them
        if source_steps_with_send_back:
            logger.info("Remapping sendBackStepId references for copied steps")

            # Build mapping from source step ID to index
            source_id_to_idx = {step["id"]: idx for idx, step in enumerate(source_steps)}

            # Get newly created step IDs from the destination
            new_steps = self._kili_api_gateway.get_steps(
                destination_project_id, ("steps.id", "steps.name")
            )

            # Build mapping from step name to new step ID
            name_to_new_id = {step["name"]: step["id"] for step in new_steps}
            idx_to_name = {idx: step["name"] for idx, step in enumerate(source_steps)}

            # Build update steps for sendBackStepId remapping
            updates_for_send_back: list[WorkflowStepUpdate] = []
            for step_idx, source_send_back_id in source_steps_with_send_back:
                target_source_idx = source_id_to_idx.get(source_send_back_id)
                if target_source_idx is None:
                    logger.warning(
                        "Could not find source step for sendBackStepId %s, skipping",
                        source_send_back_id,
                    )
                    continue

                step_name = idx_to_name[step_idx]
                target_name = idx_to_name[target_source_idx]
                new_step_id = name_to_new_id.get(step_name)
                new_target_id = name_to_new_id.get(target_name)

                if new_step_id and new_target_id:
                    updates_for_send_back.append(
                        {
                            "id": new_step_id,
                            "send_back_step_id": new_target_id,
                        }
                    )

            if updates_for_send_back:
                result = self._kili_api_gateway.update_project_workflow(
                    destination_project_id,
                    ProjectWorkflowDataKiliAPIGatewayInput(
                        enforce_step_separation=None,
                        create_steps=None,
                        update_steps=updates_for_send_back,
                        delete_steps=None,
                    ),
                )

        logger.info(
            "Successfully copied workflow from project %s to project %s",
            source_project_id,
            destination_project_id,
        )
        return result
