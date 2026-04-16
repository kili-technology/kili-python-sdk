"""Module for common argument validators across client methods."""

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
    """Convert a list of (step_name, step_status) tuples to (step_id, step_status) tuples."""
    step_name_to_id = {step["name"]: step["id"] for step in project_steps}

    unmatched_names = [
        step_name
        for step_name, _ in step_name_and_status_filters
        if step_name not in step_name_to_id
    ]
    if unmatched_names:
        raise ValueError(f"The following step names do not match any steps: {unmatched_names}")

    return [
        (step_name_to_id[step_name], step_status)
        for step_name, step_status in step_name_and_status_filters
    ]
