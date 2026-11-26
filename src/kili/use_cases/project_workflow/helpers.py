"""Helpers shared by the project workflow use cases."""

from typing import Optional

from kili.adapters.kili_api_gateway.project_workflow.common import get_assignees_to_add_ids
from kili.exceptions import NotFound


def check_percentage(name: str, value: int) -> None:
    """Refuse a percentage out of 0 to 100."""
    if not 0 <= value <= 100:
        raise ValueError(f"The parameter {name} must be between 0 and 100 (included).")


def assignee_ids_of(
    members: list[dict], emails: list[str], step_type: str, step_name: str
) -> list[str]:
    """The ids of the members to assign to a step: a review takes those who can review."""
    ids = get_assignees_to_add_ids(members, emails, exclude_labelers=step_type == "REVIEW")
    if not ids:
        raise ValueError(
            f"None of the assignees given can be assigned to step '{step_name}': a step needs"
            " at least one activated member of the project"
            + (", who is not a labeler" if step_type == "REVIEW" else "")
        )
    return ids


def find_by_id(items: Optional[list[dict]], item_id: str, kind: str) -> dict[str, object]:
    """The item of `items` that has the given id."""
    item = next((item for item in items or [] if item.get("id") == item_id), None)
    if item is None:
        raise NotFound(f"{kind} {item_id}")
    return item
