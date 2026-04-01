"""Project use cases."""

import logging
from typing import Literal, Optional, cast

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
        enforce_step_separation: Optional[bool] = None,
        create_steps: Optional[list[WorkflowStepCreate]] = None,
        update_steps: Optional[list[WorkflowStepUpdate]] = None,
        delete_steps: Optional[list[str]] = None,
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
        if source_project_id == destination_project_id:
            raise ValueError(
                "Source and destination project IDs must be different."
                f" Got the same ID: {source_project_id}"
            )

        # 1. Fetch source workflow steps and settings
        logger.info("Fetching workflow steps from source project %s", source_project_id)
        source_steps = self._kili_api_gateway.get_steps(source_project_id, _SOURCE_STEP_FIELDS)

        if not source_steps:
            raise ValueError(f"Source project {source_project_id} has no workflow steps to copy.")

        step_names = [step["name"] for step in source_steps]
        if len(step_names) != len(set(step_names)):
            raise ValueError(
                f"Source project {source_project_id} has duplicate step names."
                " Cannot reliably copy workflow with duplicate step names."
            )

        source_project = self._kili_api_gateway.get_project(
            project_id=source_project_id, fields=["enforceStepSeparation"]
        )
        enforce_step_separation: bool | None = source_project.get("enforceStepSeparation")

        # 2. Validate destination project is workflow V2
        self._validate_destination_is_workflow_v2(destination_project_id)

        # 3. Validate destination has no labels
        self._validate_destination_has_no_labels(destination_project_id)

        # 3b. Validate destination has enough labelers for the most demanding consensus step
        self._validate_consensus_labelers(destination_project_id, source_steps)

        # 4. Get existing destination steps and activated users
        dest_steps = self._get_destination_steps(destination_project_id)
        dest_users = self._kili_api_gateway.list_activated_project_users(
            str(destination_project_id)
        )
        labeler_ids = [str(u["user"]["id"]) for u in dest_users]
        reviewer_ids = [str(u["user"]["id"]) for u in dest_users if u.get("role") != "LABELER"]

        # 5. Build operations:
        # - Update the first dest step (cannot delete it) with first source step properties
        # - Delete remaining dest steps
        # - Create remaining source steps (index 1+) with destination assignees
        first_dest_step = dest_steps[0] if dest_steps else None

        update_steps: list[WorkflowStepUpdate] = []
        steps_to_create: list[WorkflowStepCreate] = []
        source_steps_with_send_back: list[tuple[str, str]] = []  # (step_name, source_send_back_id)

        if first_dest_step:
            update_steps = [_build_step_update(str(first_dest_step["id"]), source_steps[0])]
            if source_steps[0].get("sendBackStepId"):
                source_steps_with_send_back.append(
                    (str(source_steps[0]["name"]), str(source_steps[0]["sendBackStepId"]))
                )
            for step in source_steps[1:]:
                assignees = labeler_ids if step.get("type") == "DEFAULT" else reviewer_ids
                steps_to_create.append(_make_create_step(step, assignees))
                if step.get("sendBackStepId"):
                    source_steps_with_send_back.append(
                        (str(step["name"]), str(step["sendBackStepId"]))
                    )
        else:
            # No existing dest steps — create all source steps with destination assignees
            for step in source_steps:
                assignees = labeler_ids if step.get("type") == "DEFAULT" else reviewer_ids
                steps_to_create.append(_make_create_step(step, assignees))
                if step.get("sendBackStepId"):
                    source_steps_with_send_back.append(
                        (str(step["name"]), str(step["sendBackStepId"]))
                    )

        delete_steps = [str(step["id"]) for step in dest_steps[1:]] or None

        # 5. Execute: update first step + delete old extras + create new steps
        logger.info(
            "Copying %d steps from project %s to project %s",
            len(source_steps),
            source_project_id,
            destination_project_id,
        )

        result = self._kili_api_gateway.update_project_workflow(
            destination_project_id,
            ProjectWorkflowDataKiliAPIGatewayInput(
                enforce_step_separation=enforce_step_separation,
                create_steps=steps_to_create or None,
                update_steps=update_steps or None,
                delete_steps=delete_steps,
                null_fields=frozenset({"consensusCoverage", "numberOfExpectedLabelsForConsensus"}),
            ),
        )

        # 6. Remap sendBackStepId references if any steps had them
        if source_steps_with_send_back:
            remap_result = self._remap_send_back_step_ids(
                source_steps, source_steps_with_send_back, destination_project_id
            )
            if remap_result:
                result = remap_result

        logger.info(
            "Successfully copied workflow from project %s to project %s",
            source_project_id,
            destination_project_id,
        )
        return result

    def _validate_consensus_labelers(
        self, destination_project_id: ProjectId, source_steps: list[dict[str, object]]
    ) -> None:
        """Validate the destination has enough activated labelers for every consensus step."""
        required = max(
            (
                cast("int", step.get("numberOfExpectedLabelsForConsensus"))
                for step in source_steps
                if step.get("numberOfExpectedLabelsForConsensus")
            ),
            default=0,
        )

        if not required:
            return
        activated_count = self._kili_api_gateway.count_activated_project_users(
            str(destination_project_id)
        )
        if activated_count < required:
            raise ValueError(
                f"Destination project {destination_project_id} has {activated_count} activated"
                f" labeler(s), but the source workflow requires {required} for consensus."
                " Add more labelers before copying the workflow."
            )

    def _validate_destination_is_workflow_v2(self, destination_project_id: ProjectId) -> None:
        """Validate that the destination project uses workflow V2."""
        project = self._kili_api_gateway.get_project(
            project_id=destination_project_id, fields=["workflowVersion"]
        )
        version = project.get("workflowVersion")
        if version != "V2":
            raise ValueError(
                f"Destination project {destination_project_id} uses workflow version"
                f" '{version}'. Only workflow V2 projects support multi-step workflows."
            )

    def _validate_destination_has_no_labels(self, destination_project_id: ProjectId) -> None:
        """Validate that the destination project has no labels."""
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

    def _get_destination_steps(self, destination_project_id: ProjectId) -> list[dict[str, object]]:
        """Get existing steps from the destination project."""
        logger.info(
            "Fetching existing steps from destination project %s",
            destination_project_id,
        )
        try:
            return self._kili_api_gateway.get_steps(
                destination_project_id, ("steps.id", "steps.name")
            )
        except (ValueError, KeyError) as exc:
            logger.warning(
                "Could not fetch existing steps from destination project %s: %s",
                destination_project_id,
                exc,
            )
            return []

    def _remap_send_back_step_ids(
        self,
        source_steps: list[dict[str, object]],
        source_steps_with_send_back: list[tuple[str, str]],
        destination_project_id: ProjectId,
    ) -> dict[str, object]:
        """Remap sendBackStepId references from source to new destination step IDs."""
        logger.info("Remapping sendBackStepId references for copied steps")

        source_id_to_name = {str(step["id"]): str(step["name"]) for step in source_steps}
        new_steps = self._kili_api_gateway.get_steps(
            destination_project_id, ("steps.id", "steps.name")
        )
        name_to_new_id = {str(step["name"]): str(step["id"]) for step in new_steps}

        updates = _build_send_back_updates(
            source_steps_with_send_back, source_id_to_name, name_to_new_id
        )

        if updates:
            return self._kili_api_gateway.update_project_workflow(
                destination_project_id,
                ProjectWorkflowDataKiliAPIGatewayInput(
                    enforce_step_separation=None,
                    create_steps=None,
                    update_steps=updates,
                    delete_steps=None,
                ),
            )
        return {}

    def add_review_step(
        self,
        project_id: str,
        step_name: str,
        assignees: list[str],
        step_coverage: int | None = None,
        use_honeypot: bool | None = None,
        send_back_to_step: str | None = None,
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
        if consensus_coverage and not 0 <= consensus_coverage <= 100:
            raise ValueError(
                "The parameter consensus_coverage must be between 0 and 100 (included)."
            )
        steps = self._kili_api_gateway.get_steps(
            project_id=ProjectId(project_id), fields=["steps.id", "steps.name"]
        )
        step_id = next((step["id"] for step in steps if step["name"] == step_name), None)
        if step_id is None:
            raise ValueError(f"Step '{step_name}' not found")
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
        step_name: str,
        assignees: list[str] | None = None,
        step_coverage: int | None = None,
        send_back_to_step: str | None = None,
        use_honeypot: bool | None = None,
    ) -> dict[str, object]:
        """Update properties of a review step."""
        if step_coverage and not 0 <= step_coverage <= 100:
            raise ValueError("The parameter step_coverage must be between 0 and 100 (included).")
        steps = self._kili_api_gateway.get_steps(
            project_id=ProjectId(project_id), fields=["steps.id", "steps.name"]
        )
        step_id = next((step["id"] for step in steps if step["name"] == step_name), None)
        if step_id is None:
            raise ValueError(f"Step '{step_name}' not found")
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
        step_name: str,
        new_name: str,
    ) -> dict[str, object]:
        """Rename a step in a project workflow."""
        steps = self._kili_api_gateway.get_steps(
            project_id=ProjectId(project_id), fields=["steps.id", "steps.name"]
        )
        step_id = next((step["id"] for step in steps if step["name"] == step_name), None)
        if step_id is None:
            raise ValueError(f"Step '{step_name}' not found")
        data = RenameStepInput(project_id=project_id, step_id=str(step_id), new_name=new_name)
        return self._kili_api_gateway.rename_step(data)


def _make_create_step(step: dict[str, object], assignees: list[str]) -> WorkflowStepCreate:
    """Build a WorkflowStepCreate from a source step with destination project assignees.

    For DEFAULT steps, assignees are all activated project users.
    For REVIEW steps, assignees are activated project users with role != LABELER.
    """
    create_step: WorkflowStepCreate = {
        "name": cast("str", step["name"]),
        "type": cast("Literal['DEFAULT', 'REVIEW']", step["type"]),
        "assignees": assignees,
    }
    if step.get("consensusCoverage") is not None:
        create_step["consensus_coverage"] = cast("int", step["consensusCoverage"])
    if step.get("numberOfExpectedLabelsForConsensus") is not None:
        create_step["number_of_expected_labels_for_consensus"] = cast(
            "int", step["numberOfExpectedLabelsForConsensus"]
        )
    if step.get("stepCoverage") is not None:
        create_step["step_coverage"] = cast("int", step["stepCoverage"])
    return create_step


def _build_step_update(dest_step_id: str, source_step: dict[str, object]) -> WorkflowStepUpdate:
    """Build a WorkflowStepUpdate for the first dest step based on source step properties."""
    return {
        "id": dest_step_id,
        "name": cast("str", source_step["name"]),
        "consensus_coverage": cast("int | None", source_step.get("consensusCoverage")),
        "number_of_expected_labels_for_consensus": cast(
            "int | None", source_step.get("numberOfExpectedLabelsForConsensus")
        ),
    }


def _build_send_back_updates(
    source_steps_with_send_back: list[tuple[str, str]],
    source_id_to_name: dict[str, str],
    name_to_new_id: dict[str, str],
) -> list[WorkflowStepUpdate]:
    """Build WorkflowStepUpdate list for sendBackStepId remapping."""
    updates: list[WorkflowStepUpdate] = []
    for step_name, source_send_back_id in source_steps_with_send_back:
        target_name = source_id_to_name.get(source_send_back_id)
        if target_name is None:
            logger.warning(
                "Could not find source step for sendBackStepId %s, skipping",
                source_send_back_id,
            )
            continue

        new_step_id = name_to_new_id.get(step_name)
        new_target_id = name_to_new_id.get(target_name)

        if new_step_id and new_target_id:
            updates.append({"id": new_step_id, "send_back_step_id": new_target_id})
    return updates
