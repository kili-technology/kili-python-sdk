"""Project Workflow gateway common."""

import warnings
from collections.abc import Mapping
from typing import Optional, Union, cast


def get_assignees_to_add_ids(
    existing_members: list[dict], assignees: list[str], exclude_labelers: bool = True
) -> list:
    """Get list of assignees ids to add.

    A review takes members who can review, so labelers are left out unless `exclude_labelers` is
    False, as for a labeling step.
    """
    members_by_email = {m["user"]["email"]: m for m in (existing_members or [])}
    assignees_to_add = []
    assignees_added = []
    assignees_not_added = []
    for email in assignees:
        member = members_by_email.get(email)
        if member and (not exclude_labelers or member.get("role") != "LABELER"):
            user_id = member["user"]["id"]
            assignees_to_add.append(user_id)
            assignees_added.append(email)
        else:
            assignees_not_added.append(email)
    if assignees_not_added:
        reason = "not found or can not review" if exclude_labelers else "not project members"
        warnings.warn(f"These emails were not added ({reason}): " + ", ".join(assignees_not_added))
    return assignees_to_add


def find_step_group_by_name(project: dict, group_name: str) -> dict:
    """Find a step group of a multi-group workflow project by its name."""
    if project.get("workflowVersion") != "V3":
        raise ValueError("group_name is only supported in the multi-group workflow")
    group = next(
        (
            step_group
            for step_group in project.get("stepGroups") or []
            if step_group.get("name") == group_name
        ),
        None,
    )
    if group is None:
        raise ValueError(f"Group '{group_name}' not found in project workflow")
    return group


def find_step_by_name(project: dict, step_name: str, group_name: Optional[str]) -> dict:
    """Find a workflow step by name, optionally scoped to a step group.

    When group_name is provided, the lookup is restricted to the named group and only supported
    on multi-group workflow projects. When group_name is None, the step name must be unique across all
    groups, otherwise the caller is asked to provide a group_name.
    """
    steps = project.get("steps") or []

    if group_name is not None:
        group = find_step_group_by_name(project, group_name)
        target_step = next(
            (
                step
                for step in steps
                if step.get("name") == step_name and step.get("stepGroupId") == group.get("id")
            ),
            None,
        )
        if target_step is None:
            raise ValueError(f"Step '{step_name}' not found in group '{group_name}'")
        return target_step

    matching_steps = [step for step in steps if step.get("name") == step_name]
    if not matching_steps:
        raise ValueError(f"Step '{step_name}' not found in project workflow")
    if len(matching_steps) > 1:
        raise ValueError(
            f"Multiple steps named '{step_name}' exist across groups; please provide group_name,"
            " or the step_id"
        )
    return matching_steps[0]


def resolve_step(
    project: dict,
    step_id: Optional[str],
    step_name: Optional[str],
    group_name: Optional[str],
) -> dict:
    """Find the workflow step designated either by its id, or by its name and group.

    Step names are unique per group only, so a step is given either by `step_id`, or by
    `step_name` with `group_name` when several groups use that name — never both ways at once.
    """
    if (step_id is None) == (step_name is None):
        raise ValueError(
            "Provide either step_id, or step_name (with group_name when several groups use it),"
            " but not both"
        )

    if step_id is None:
        return find_step_by_name(project, cast(str, step_name), group_name)

    if group_name is not None:
        raise ValueError("group_name goes with step_name only, not with step_id")
    step = next((step for step in project.get("steps") or [] if step.get("id") == step_id), None)
    if step is None:
        raise ValueError(f"Step '{step_id}' not found in project workflow")
    return step


def find_step(project: dict, step: Union[str, Mapping]) -> dict:
    """Find the workflow step given by its id, by its name, or as `{"name", "group_name"}`.

    A string is read as an id first, then as a name, which must then be unique in the project.
    The whole project is searched, whichever group the step is in.
    """
    if isinstance(step, str):
        step_by_id = next(
            (candidate for candidate in project.get("steps") or [] if candidate.get("id") == step),
            None,
        )
        if step_by_id is not None:
            return step_by_id
        return find_step_by_name(project, step, None)
    return find_step_by_name(project, step["name"], step.get("group_name"))


def find_step_group(project: dict, group: str) -> dict:
    """Find the step group of a multi-group workflow project given by its id or its name."""
    if project.get("workflowVersion") != "V3":
        raise ValueError("Step groups are only available in the multi-group workflow")
    group_by_id = next(
        (
            candidate
            for candidate in project.get("stepGroups") or []
            if candidate.get("id") == group
        ),
        None,
    )
    if group_by_id is not None:
        return group_by_id
    return find_step_group_by_name(project, group)
