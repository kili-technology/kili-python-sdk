"""Use cases of the transitions of a project workflow, for the domain client."""

from collections.abc import Sequence
from typing import NamedTuple, Optional, cast

from cuid import cuid

from kili.adapters.kili_api_gateway.project_workflow.common import find_step, find_step_group
from kili.domain.project import (
    ProjectId,
    WorkflowStepCreate,
    WorkflowStepGroupToCreate,
    WorkflowStepToCreate,
    WorkflowTransitionCondition,
    WorkflowTransitionToCreate,
    WorkflowTransitionToUpdate,
)
from kili.use_cases.base import BaseUseCases
from kili.use_cases.project_workflow.helpers import conditional_routing_required

TRANSITION_FIELDS = (
    "id",
    "fromStepId",
    "fromStepGroupId",
    "toStepId",
    "priority",
    "condition.type",
    "condition.percentage",
    "condition.jobName",
    "condition.categories",
    "condition.quantifier",
    "condition.value",
)


WORKFLOW_FIELDS = (
    "enforceStepSeparation",
    "usesConditionalRouting",
    "canEditTransitions",
    "steps.id",
    "steps.name",
    "steps.type",
    "steps.stepGroupId",
    "steps.sendBackStepId",
    "steps.sendBackToPreviousStep",
    "steps.stepCoverage",
    "steps.consensusCoverage",
    "steps.numberOfExpectedLabelsForConsensus",
    "steps.useHoneypot",
    "steps.assignees.id",
    "steps.assignees.email",
    "stepGroups.id",
    "stepGroups.name",
    "stepGroups.order",
    "stepGroups.allowedJobNames",
    *(f"workflowTransitions.{field}" for field in TRANSITION_FIELDS),
)


_TRANSITION_CONTEXT_FIELDS = (
    "workflowVersion",
    "steps.id",
    "steps.name",
    "steps.type",
    "steps.stepGroupId",
    "stepGroups.id",
    "stepGroups.name",
    *(f"workflowTransitions.{field}" for field in TRANSITION_FIELDS),
)


class WorkflowTransitionUseCases(BaseUseCases):
    """Transition use cases of the domain client."""

    def get_workflow(self, project_id: ProjectId) -> dict[str, object]:
        """Get the whole workflow of a project: its steps, step groups and transitions."""
        with conditional_routing_required("kili.projects.workflow.get()"):
            return self._kili_api_gateway.get_workflow(project_id, WORKFLOW_FIELDS)

    def list_transitions(self, project_id: ProjectId) -> list[dict[str, object]]:
        """List the transitions of a project workflow."""
        with conditional_routing_required("kili.projects.workflow.transitions.list()"):
            workflow = self._kili_api_gateway.get_workflow(
                project_id, [f"workflowTransitions.{field}" for field in TRANSITION_FIELDS]
            )
        return workflow["workflowTransitions"]

    def transitions_to_save(
        self,
        project_id: ProjectId,
        new_parts: "NewWorkflowParts",
        create_transitions: list[WorkflowTransitionToCreate],
        update_transitions: list[WorkflowTransitionToUpdate],
        delete_transitions: list[str],
    ) -> list[dict]:
        """Every transition the workflow keeps, as the API takes them.

        A stored transition is sent with its id, which keeps it and its sampling outcomes: one
        sent without it would be created again.
        """
        workflow = self._kili_api_gateway.get_workflow(project_id, _TRANSITION_CONTEXT_FIELDS)
        stored = {transition["id"]: transition for transition in workflow["workflowTransitions"]}
        deleted_step_ids = set(new_parts.deleted_step_ids) | {
            step["id"]
            for step in workflow["steps"]
            if step.get("stepGroupId") in new_parts.deleted_group_ids
        }
        context = new_parts.context_after(workflow, deleted_step_ids)

        for transition_id in delete_transitions:
            if transition_id not in stored:
                raise ValueError(f"Transition '{transition_id}' is not a transition of the project")
        gone = set(delete_transitions) | {
            transition["id"]
            for transition in stored.values()
            if transition.get("fromStepId") in deleted_step_ids
            or transition.get("toStepId") in deleted_step_ids
            or transition.get("fromStepGroupId") in new_parts.deleted_group_ids
        }

        updates: dict[str, WorkflowTransitionToUpdate] = {}
        for update in update_transitions:
            transition = stored.get(update["id"])
            if transition is None:
                raise ValueError(f"Transition '{update['id']}' is not a transition of the project")
            if update["id"] in gone:
                raise ValueError(
                    f"Transition '{update['id']}' is deleted by the same call, or leaves or enters"
                    " a step or group it deletes"
                )
            _check_same_ends(context, transition, update)
            updates[update["id"]] = update

        kept = [
            _stored_transition_input(transition, updates.get(transition_id))
            for transition_id, transition in stored.items()
            if transition_id not in gone
        ]
        return kept + [
            _new_transition_input(context, transition) for transition in create_transitions
        ]


class NewWorkflowParts(NamedTuple):
    """The steps and groups a call creates and deletes, which its transitions may name."""

    steps: Sequence[WorkflowStepCreate]
    step_groups: list[WorkflowStepGroupToCreate]
    deleted_step_ids: list[str]
    deleted_group_ids: list[str]

    def context_after(self, workflow: dict, deleted_step_ids: set[str]) -> dict:
        """The steps and groups the transitions name: the stored ones kept, and the new ones."""
        new_groups = [{"id": group.get("id"), "name": group["name"]} for group in self.step_groups]
        new_steps = [
            {"id": step.get("id"), "name": step["name"], "stepGroupId": group.get("id")}
            for group in self.step_groups
            for step in group["steps"]
        ] + [
            {
                "id": cast(dict, step).get("id"),
                "name": step["name"],
                "stepGroupId": step.get("step_group_id"),
            }
            for step in self.steps
        ]
        return {
            "workflowVersion": workflow.get("workflowVersion"),
            "steps": [step for step in workflow["steps"] if step["id"] not in deleted_step_ids]
            + new_steps,
            "stepGroups": [
                group
                for group in workflow["stepGroups"]
                if group["id"] not in self.deleted_group_ids
            ]
            + new_groups,
        }


def with_client_ids(
    create_steps: Optional[Sequence[WorkflowStepCreate]],
    create_step_groups: Optional[list[WorkflowStepGroupToCreate]],
) -> tuple[Optional[list[WorkflowStepToCreate]], Optional[list[WorkflowStepGroupToCreate]]]:
    """The steps and groups to create, each with an id of its own for the transitions to name it."""
    steps = [_with_id(step) for step in create_steps or []] or None
    groups: Optional[list[WorkflowStepGroupToCreate]] = [
        {
            **group,
            "id": group.get("id") or cuid(),
            "steps": [_with_id(step) for step in group["steps"]],
        }
        for group in create_step_groups or []
    ] or None
    return steps, groups


def _with_id(step: WorkflowStepCreate) -> WorkflowStepToCreate:
    return cast(WorkflowStepToCreate, {**step, "id": cast(dict, step).get("id") or cuid()})


def _condition_input(condition: WorkflowTransitionCondition) -> dict:
    """A condition as the API takes it."""
    fields = {
        "type": condition["type"],
        "percentage": condition.get("percentage"),
        "jobName": condition.get("job_name"),
        "categories": condition.get("categories"),
        "quantifier": condition.get("quantifier"),
        "value": condition.get("value"),
    }
    return {key: value for key, value in fields.items() if value is not None}


def _stored_transition_input(
    transition: dict, update: Optional[WorkflowTransitionToUpdate]
) -> dict:
    """A stored transition as the API takes it, with its id, and the update given to it."""
    condition = update.get("condition") if update else None
    priority = update.get("priority") if update else None
    if condition is None and transition.get("condition") is None:
        raise ValueError(
            f"Transition '{transition['id']}' has a condition the server can no longer read:"
            " delete it, or give it a new condition with update_transitions"
        )
    fields = {
        "id": transition["id"],
        "fromStepId": transition.get("fromStepId"),
        "fromStepGroupId": transition.get("fromStepGroupId"),
        "toStepId": transition.get("toStepId"),
        "priority": priority if priority is not None else transition["priority"],
        "condition": _condition_input(condition)
        if condition is not None
        else {key: value for key, value in transition["condition"].items() if value is not None},
    }
    return {key: value for key, value in fields.items() if value is not None}


def _new_transition_input(context: dict, transition: WorkflowTransitionToCreate) -> dict:
    """A transition to create as the API takes it, its steps and group given by id."""
    from_step = transition.get("from_step")
    from_step_group = transition.get("from_step_group")
    if (from_step is None) == (from_step_group is None):
        raise ValueError(
            "A transition leaves a step (from_step) or the end of a group (from_step_group):"
            " give exactly one"
        )
    to_step = transition.get("to_step")
    fields = {
        "fromStepId": find_step(context, from_step)["id"] if from_step is not None else None,
        "fromStepGroupId": find_step_group(context, from_step_group)["id"]
        if from_step_group is not None
        else None,
        "toStepId": find_step(context, to_step)["id"] if to_step is not None else None,
        "priority": transition["priority"],
        "condition": _condition_input(transition["condition"]),
    }
    return {key: value for key, value in fields.items() if value is not None}


def _check_same_ends(context: dict, transition: dict, update: WorkflowTransitionToUpdate) -> None:
    """Refuse an update that names another source or target than the transition's."""
    ends = {
        "from_step": ("fromStepId", find_step),
        "from_step_group": ("fromStepGroupId", find_step_group),
        "to_step": ("toStepId", find_step),
    }
    for key, (stored_key, find) in ends.items():
        if key not in update:
            continue
        given = cast(dict, update)[key]
        given_id = find(context, given)["id"] if given is not None else None
        if given_id != transition.get(stored_key):
            raise ValueError(
                f"Transition '{transition['id']}' keeps its source and target: to change them,"
                " delete it and create another"
            )
