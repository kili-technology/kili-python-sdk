"""Project Workflow gateway common."""

import warnings
from typing import Optional


def get_assignees_to_add_ids(existing_members: list[dict], assignees: list[str]) -> list:
    """Get list of assignees ids to add."""
    members_by_email = {m["user"]["email"]: m for m in (existing_members or [])}
    assignees_to_add = []
    assignees_added = []
    assignees_not_added = []
    for email in assignees:
        member = members_by_email.get(email)
        if member and member.get("role") != "LABELER":
            user_id = member["user"]["id"]
            assignees_to_add.append(user_id)
            assignees_added.append(email)
        else:
            assignees_not_added.append(email)
    if assignees_not_added:
        warnings.warn(
            "These emails were not added (not found or can not review): "
            + ", ".join(assignees_not_added)
        )
    return assignees_to_add


def find_step_by_name(project: dict, step_name: str, group_name: Optional[str]) -> dict:
    """Find a workflow step by name, optionally scoped to a step group.

    When group_name is provided, the lookup is restricted to the named group and only supported
    on workflow V3 projects. When group_name is None, the step name must be unique across all
    groups, otherwise the caller is asked to provide a group_name.
    """
    steps = project.get("steps") or []

    if group_name is not None:
        if project.get("workflowVersion") != "V3":
            raise ValueError("group_name is only supported on workflow V3 projects")
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
            f"Multiple steps named '{step_name}' exist across groups; please provide group_name"
        )
    return matching_steps[0]
