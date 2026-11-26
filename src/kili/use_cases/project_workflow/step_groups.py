"""Use cases of the step groups of a project workflow."""

from typing import Optional

from cuid import cuid

from kili.adapters.kili_api_gateway.project_workflow.common import find_step_group
from kili.adapters.kili_api_gateway.project_workflow.types import (
    ProjectWorkflowDataKiliAPIGatewayInput,
)
from kili.domain.project import ProjectId, WorkflowStepGroupToCreate
from kili.use_cases.base import BaseUseCases
from kili.use_cases.project_workflow.helpers import assignee_ids_of, check_percentage, find_by_id

STEP_GROUP_FIELDS = (
    "stepGroups.id",
    "stepGroups.name",
    "stepGroups.order",
    "stepGroups.allowedJobNames",
    "stepGroups.steps.id",
    "stepGroups.steps.name",
    "stepGroups.steps.type",
)


class WorkflowStepGroupUseCases(BaseUseCases):
    """Step group use cases, in the multi-group workflow."""

    def list_step_groups(self, project_id: ProjectId) -> list[dict[str, object]]:
        """List the step groups of a project workflow, with their steps."""
        return self._kili_api_gateway.get_step_groups(project_id, STEP_GROUP_FIELDS)

    def create_step_group(
        self,
        project_id: ProjectId,
        name: str,
        labeling_step_name: str,
        labelers: list[str],
        review_step_name: str,
        reviewers: list[str],
        sample_percentage: int,
        allowed_job_names: Optional[list[str]] = None,
    ) -> dict[str, object]:
        """Create a step group with its labeling step and its first review, in one call."""
        check_percentage("sample_percentage", sample_percentage)
        members = self._kili_api_gateway.list_activated_project_users(project_id)
        group_id = cuid()
        group: WorkflowStepGroupToCreate = {
            "id": group_id,
            "name": name,
            "allowed_job_names": allowed_job_names,
            "steps": [
                {
                    "id": cuid(),
                    "type": "DEFAULT",
                    "name": labeling_step_name,
                    "assignees": assignee_ids_of(members, labelers, "DEFAULT", labeling_step_name),
                },
                {
                    "id": cuid(),
                    "type": "REVIEW",
                    "name": review_step_name,
                    "assignees": assignee_ids_of(members, reviewers, "REVIEW", review_step_name),
                    "step_coverage": sample_percentage,
                },
            ],
        }
        result = self._kili_api_gateway.update_project_workflow(
            project_id,
            ProjectWorkflowDataKiliAPIGatewayInput(
                enforce_step_separation=None,
                create_steps=None,
                update_steps=None,
                delete_steps=None,
                create_step_groups=[group],
            ),
            fields=STEP_GROUP_FIELDS,
        )
        return find_by_id(result.get("stepGroups"), group_id, "step group")

    def update_step_group(
        self,
        project_id: ProjectId,
        group: str,
        name: Optional[str] = None,
        allowed_job_names: Optional[list[str]] = None,
    ) -> dict[str, object]:
        """Rename a step group or change the jobs it allows."""
        if name is None and allowed_job_names is None:
            raise ValueError("Give the new name of the group, or its allowed job names")
        context = self._kili_api_gateway.get_project_workflow_context(project_id)
        group_id = find_step_group(context, group)["id"]
        result = self._kili_api_gateway.update_project_workflow(
            project_id,
            ProjectWorkflowDataKiliAPIGatewayInput(
                enforce_step_separation=None,
                create_steps=None,
                update_steps=None,
                delete_steps=None,
                update_step_groups=[
                    {"id": group_id, "name": name, "allowed_job_names": allowed_job_names}
                ],
            ),
            fields=STEP_GROUP_FIELDS,
        )
        return find_by_id(result.get("stepGroups"), group_id, "step group")

    def delete_step_group(self, project_id: ProjectId, group: str) -> dict[str, str]:
        """Delete a step group with its steps."""
        context = self._kili_api_gateway.get_project_workflow_context(project_id)
        group_id = find_step_group(context, group)["id"]
        self._kili_api_gateway.update_project_workflow(
            project_id,
            ProjectWorkflowDataKiliAPIGatewayInput(
                enforce_step_separation=None,
                create_steps=None,
                update_steps=None,
                delete_steps=None,
                delete_step_groups=[group_id],
            ),
            fields=["stepGroups{id}"],
        )
        return {"id": group_id}
