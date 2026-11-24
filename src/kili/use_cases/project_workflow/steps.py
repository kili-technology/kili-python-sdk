"""Use cases of the steps of a project workflow, for the domain client."""

from typing import Literal, Optional, Union

from cuid import cuid

from kili.adapters.kili_api_gateway.project_workflow.common import (
    find_step,
    find_step_group_by_name,
)
from kili.adapters.kili_api_gateway.project_workflow.types import (
    AddReviewStepInput,
    ProjectWorkflowDataKiliAPIGatewayInput,
)
from kili.domain.project import (
    ProjectId,
    WorkflowStepDesignation,
    WorkflowStepToCreate,
    WorkflowStepToUpdate,
)
from kili.exceptions import NotFound
from kili.use_cases.base import BaseUseCases
from kili.use_cases.project_workflow.helpers import assignee_ids_of, check_percentage, find_by_id

# What the domain client answers for a step, as the method client's get_steps does by default.
STEP_FIELDS = (
    "steps.type",
    "steps.name",
    "steps.id",
    "steps.stepGroupId",
    "steps.assignees.email",
    "steps.assignees.id",
)


class WorkflowStepUseCases(BaseUseCases):
    """Step use cases of the domain client."""

    def list_steps(self, project_id: ProjectId) -> list[dict[str, object]]:
        """List the steps of a project workflow."""
        return self._kili_api_gateway.get_steps(project_id, STEP_FIELDS)

    def create_step(
        self,
        project_id: ProjectId,
        name: str,
        assignees: list[str],
        group_name: Optional[str] = None,
        step_type: Literal["DEFAULT", "REVIEW"] = "REVIEW",
        sample_percentage: Optional[int] = None,
        send_back_to_step: Optional[Union[str, WorkflowStepDesignation]] = None,
        consensus_coverage: Optional[int] = None,
        number_of_expected_labels_for_consensus: Optional[int] = None,
        use_honeypot: Optional[bool] = None,
    ) -> dict[str, object]:
        """Create a step at the end of its group.

        A review goes through addReviewStep, the only input taking a honeypot at creation; a
        labeling step through editProjectWorkflowSettings, the only one creating it.
        """
        if step_type == "REVIEW":
            if sample_percentage is None:
                raise ValueError(
                    "sample_percentage is required to create a review: the percentage of the"
                    " assets of its group that it reviews, from 0 to 100"
                )
            check_percentage("sample_percentage", sample_percentage)
            if (
                consensus_coverage is not None
                or number_of_expected_labels_for_consensus is not None
            ):
                raise ValueError("Consensus is set on a labeling step, not on a review")
        else:
            if sample_percentage is not None:
                raise ValueError(
                    "sample_percentage is set on a review: a labeling step takes every asset"
                    " that reaches it"
                )
            if send_back_to_step is not None:
                raise ValueError("send_back_to_step is set on a review, not on a labeling step")
            if use_honeypot is not None:
                raise ValueError(
                    "use_honeypot cannot be given at a labeling step's creation: set it with"
                    " kili.projects.workflow.steps.update() once the step exists"
                )
            if consensus_coverage is not None:
                check_percentage("consensus_coverage", consensus_coverage)

        context = self._kili_api_gateway.get_project_workflow_context(project_id)
        group_id = _group_id_for_new_step(context, group_name)
        send_back_step_id = (
            find_step(context, send_back_to_step)["id"] if send_back_to_step is not None else None
        )
        members = self._kili_api_gateway.list_activated_project_users(project_id)
        assignee_ids = assignee_ids_of(members, assignees, step_type, name)

        if step_type == "REVIEW":
            result = self._kili_api_gateway.create_review_step(
                AddReviewStepInput(
                    project_id=project_id,
                    step_name=name,
                    assignees=assignee_ids,
                    step_coverage=sample_percentage,
                    use_honeypot=use_honeypot,
                    send_back_to_step=send_back_step_id,
                    step_group_id=group_id,
                ),
                fields=STEP_FIELDS,
            )
            return _new_step(result, name, group_id)

        step_id = cuid()
        step: WorkflowStepToCreate = {
            "id": step_id,
            "type": "DEFAULT",
            "name": name,
            "assignees": assignee_ids,
            "step_group_id": group_id,
            "consensus_coverage": consensus_coverage,
            "number_of_expected_labels_for_consensus": number_of_expected_labels_for_consensus,
        }
        result = self._kili_api_gateway.update_project_workflow(
            project_id,
            ProjectWorkflowDataKiliAPIGatewayInput(
                enforce_step_separation=None,
                create_steps=[step],
                update_steps=None,
                delete_steps=None,
            ),
            fields=STEP_FIELDS,
        )
        return find_by_id(result.get("steps"), step_id, "step")

    def update_step(
        self,
        project_id: ProjectId,
        step: Union[str, WorkflowStepDesignation],
        name: Optional[str] = None,
        consensus_coverage: Optional[int] = None,
        number_of_expected_labels_for_consensus: Optional[int] = None,
        use_honeypot: Optional[bool] = None,
        send_back_to_step: Optional[Union[str, WorkflowStepDesignation]] = None,
    ) -> dict[str, object]:
        """Update the properties of a step, refusing those that do not fit its type."""
        context = self._kili_api_gateway.get_project_workflow_context(project_id)
        target = find_step(context, step)
        has_consensus = (
            consensus_coverage is not None or number_of_expected_labels_for_consensus is not None
        )
        if target.get("type") == "DEFAULT" and send_back_to_step is not None:
            raise ValueError(
                f"send_back_to_step is set on a review: step '{target['name']}' is a labeling step"
            )
        if target.get("type") == "REVIEW" and has_consensus:
            raise ValueError(
                f"Consensus is set on a labeling step: step '{target['name']}' is a review"
            )
        if consensus_coverage is not None:
            check_percentage("consensus_coverage", consensus_coverage)
        if (
            name is None
            and not has_consensus
            and use_honeypot is None
            and send_back_to_step is None
        ):
            raise ValueError("Give at least one property of the step to change")

        update: WorkflowStepToUpdate = {
            "id": target["id"],
            "name": name,
            "consensus_coverage": consensus_coverage,
            "number_of_expected_labels_for_consensus": number_of_expected_labels_for_consensus,
            "use_honeypot": use_honeypot,
            "send_back_step_id": (
                find_step(context, send_back_to_step)["id"]
                if send_back_to_step is not None
                else None
            ),
        }
        result = self._kili_api_gateway.update_project_workflow(
            project_id,
            ProjectWorkflowDataKiliAPIGatewayInput(
                enforce_step_separation=None,
                create_steps=None,
                update_steps=[update],
                delete_steps=None,
            ),
            fields=STEP_FIELDS,
        )
        return find_by_id(result.get("steps"), target["id"], "step")

    def delete_step(
        self, project_id: ProjectId, step: Union[str, WorkflowStepDesignation]
    ) -> dict[str, str]:
        """Delete a step, whichever its place in its group."""
        context = self._kili_api_gateway.get_project_workflow_context(project_id)
        step_id = find_step(context, step)["id"]
        self._kili_api_gateway.update_project_workflow(
            project_id,
            ProjectWorkflowDataKiliAPIGatewayInput(
                enforce_step_separation=None,
                create_steps=None,
                update_steps=None,
                delete_steps=[step_id],
            ),
            fields=["steps{id}"],
        )
        return {"id": step_id}


def _group_id_for_new_step(context: dict, group_name: Optional[str]) -> Optional[str]:
    """The id of the group a new step goes to: the one named, else the project's only one."""
    if group_name is not None:
        return find_step_group_by_name(context, group_name)["id"]
    if context.get("workflowVersion") != "V3":
        return None
    groups = context.get("stepGroups") or []
    if len(groups) != 1:
        raise ValueError("The project has several groups: give the group_name of the new step")
    return groups[0]["id"]


def _new_step(result: dict, name: str, group_id: Optional[str]) -> dict[str, object]:
    # addReviewStep takes no id: the new step is the one of that name in its group.
    step = next(
        (
            step
            for step in result.get("steps") or []
            if step.get("name") == name and group_id in (None, step.get("stepGroupId"))
        ),
        None,
    )
    if step is None:
        raise NotFound(f"step {name}")
    return step
