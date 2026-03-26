"""Project use cases."""

import logging
from typing import Optional

from kili.adapters.kili_api_gateway.project_workflow.types import (
    ProjectWorkflowDataKiliAPIGatewayInput,
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

        # 1. Fetch source workflow steps
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

        # 2. Validate destination project is workflow V2
        self._validate_destination_is_workflow_v2(destination_project_id)

        # 3. Validate destination has no labels
        self._validate_destination_has_no_labels(destination_project_id)

        # 4. Get existing destination steps
        dest_steps = self._get_destination_steps(destination_project_id)

        # 5. Build operations:
        # - Update the first dest step (cannot delete it) with first source step properties
        # - Delete remaining dest steps
        # - Create remaining source steps (index 1+)
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
                steps_to_create.append(_make_create_step(step))
                if step.get("sendBackStepId"):
                    source_steps_with_send_back.append(
                        (str(step["name"]), str(step["sendBackStepId"]))
                    )
        else:
            # No existing dest steps — create all source steps
            for step in source_steps:
                steps_to_create.append(_make_create_step(step))
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
                enforce_step_separation=None,
                create_steps=steps_to_create or None,
                update_steps=update_steps or None,
                delete_steps=delete_steps,
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


def _make_create_step(step: dict[str, object]) -> WorkflowStepCreate:
    """Build a WorkflowStepCreate from a source step. Assignees are omitted (backend default)."""
    create_step: WorkflowStepCreate = {
        "name": step["name"],
        "type": step["type"],
    }
    if step.get("consensusCoverage") is not None:
        create_step["consensus_coverage"] = step["consensusCoverage"]
    if step.get("numberOfExpectedLabelsForConsensus") is not None:
        create_step["number_of_expected_labels_for_consensus"] = step[
            "numberOfExpectedLabelsForConsensus"
        ]
    if step.get("stepCoverage") is not None:
        create_step["step_coverage"] = step["stepCoverage"]
    return create_step


def _build_step_update(dest_step_id: str, source_step: dict[str, object]) -> WorkflowStepUpdate:
    """Build a WorkflowStepUpdate for the first dest step based on source step properties."""
    update: WorkflowStepUpdate = {
        "id": dest_step_id,
        "name": source_step["name"],
        "type": source_step["type"],
    }
    if source_step.get("consensusCoverage") is not None:
        update["consensus_coverage"] = source_step["consensusCoverage"]
    if source_step.get("numberOfExpectedLabelsForConsensus") is not None:
        update["number_of_expected_labels_for_consensus"] = source_step[
            "numberOfExpectedLabelsForConsensus"
        ]
    if source_step.get("stepCoverage") is not None:
        update["step_coverage"] = source_step["stepCoverage"]
    return update


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
