"""Module for common argument validators across client methods."""

from typing import Optional

from kili.domain.asset.asset import StatusInStep
from kili.domain.project import ProjectStep


def extract_step_ids_from_project_steps(
    project_steps: list[ProjectStep],
    step_name_in: list[str],
) -> list[str]:
    """Extract step ids from project steps."""
    matching_steps = [step for step in project_steps if step["name"] in step_name_in]

    # Raise an exception if any name in step_name_in does not match a step["name"]
    unmatched_names = [
        name for name in step_name_in if name not in [step["name"] for step in project_steps]
    ]
    if unmatched_names:
        raise ValueError(f"The following step names do not match any steps: {unmatched_names}")

    return [step["id"] for step in matching_steps]


def extract_step_id_and_status_filters_from_project_steps(
    project_steps: list[ProjectStep],
    step_name_and_status_filters: list[tuple[str, StatusInStep]],
) -> list[tuple[str, StatusInStep]]:
    """Convert a list of (step_name, step_status) tuples to (step_id, step_status) tuples.

    Step names are unique per group only: a name several groups use stands for the step of each of
    them, the same way `extract_step_ids_from_project_steps` reads it, and `group_name_in` is what
    narrows it down to one group.
    """
    step_ids_by_name: dict[str, list[str]] = {}
    for step in project_steps:
        step_ids_by_name.setdefault(step["name"], []).append(step["id"])

    unmatched_names = [
        step_name
        for step_name, _ in step_name_and_status_filters
        if step_name not in step_ids_by_name
    ]
    if unmatched_names:
        raise ValueError(f"The following step names do not match any steps: {unmatched_names}")

    return [
        (step_id, step_status)
        for step_name, step_status in step_name_and_status_filters
        for step_id in step_ids_by_name[step_name]
    ]


def resolve_step_filters(
    project_steps: list[ProjectStep],
    *,
    step_id_in: Optional[list[str]],
    step_id_not_in: Optional[list[str]],
    step_id_and_status_in: Optional[list[tuple[str, StatusInStep]]],
    step_id_and_status_not_in: Optional[list[tuple[str, StatusInStep]]],
    step_name_in: Optional[list[str]],
    step_name_not_in: Optional[list[str]],
    step_name_and_status_in: Optional[list[tuple[str, StatusInStep]]],
    step_name_and_status_not_in: Optional[list[tuple[str, StatusInStep]]],
) -> tuple[
    Optional[list[str]],
    Optional[list[str]],
    Optional[list[tuple[str, StatusInStep]]],
    Optional[list[tuple[str, StatusInStep]]],
]:
    """The step filters by id, each given either by id or by name, never both ways at once.

    Returns (step_id_in, step_id_not_in, step_id_and_status_in, step_id_and_status_not_in).
    """
    for by_id, by_name, suffix in (
        (step_id_in, step_name_in, "in"),
        (step_id_not_in, step_name_not_in, "not_in"),
        (step_id_and_status_in, step_name_and_status_in, "and_status_in"),
        (step_id_and_status_not_in, step_name_and_status_not_in, "and_status_not_in"),
    ):
        if by_id is not None and by_name is not None:
            raise ValueError(
                f"Filters step_id_{suffix} and step_name_{suffix} both given: use only one of them."
            )

    return (
        step_id_in
        if step_name_in is None
        else extract_step_ids_from_project_steps(project_steps, step_name_in),
        step_id_not_in
        if step_name_not_in is None
        else extract_step_ids_from_project_steps(project_steps, step_name_not_in),
        step_id_and_status_in
        if step_name_and_status_in is None
        else extract_step_id_and_status_filters_from_project_steps(
            project_steps, step_name_and_status_in
        ),
        step_id_and_status_not_in
        if step_name_and_status_not_in is None
        else extract_step_id_and_status_filters_from_project_steps(
            project_steps, step_name_and_status_not_in
        ),
    )
