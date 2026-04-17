"""Project Workflow gateway common."""

import warnings


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
