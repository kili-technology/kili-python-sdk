"""Module for common argument validators across client methods."""

from typing import List

from kili.domain.project import ProjectStep


def extract_step_ids_from_project_steps(
    project_steps: List[ProjectStep],
    step_name_in: List[str],
) -> List[str]:
    """Extract step ids from project steps."""
    matching_steps = [step for step in project_steps if step["name"] in step_name_in]

    # Raise an exception if any name in step_name_in does not match a step["name"]
    unmatched_names = [
        name for name in step_name_in if name not in [step["name"] for step in project_steps]
    ]
    if unmatched_names:
        raise ValueError(f"The following step names do not match any steps: {unmatched_names}")

    return [step["id"] for step in matching_steps]
