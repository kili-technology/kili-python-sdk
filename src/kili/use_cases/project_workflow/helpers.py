"""Helpers shared by the project workflow use cases."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Optional

from kili.adapters.kili_api_gateway.project_workflow.common import get_assignees_to_add_ids
from kili.exceptions import GraphQLError, NotFound

# How a GraphQL server refuses a field, an argument or an input field it does not know.
_UNKNOWN_TO_THE_SERVER = ("Cannot query field", "Unknown argument", "is not defined by type")


@contextmanager
def conditional_routing_required(method: str) -> Iterator[None]:
    """Explain the refusal of a Kili server that predates the conditional routing workflow."""
    try:
        yield
    except GraphQLError as error:
        if any(marker in str(error) for marker in _UNKNOWN_TO_THE_SERVER):
            raise GraphQLError(
                f"{method} needs a version of Kili that serves the conditional routing workflow"
                f" (LAB-4823), which this Kili server does not: {error}"
            ) from error
        raise


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
