"""Module for common argument validators across client methods."""

import warnings
from typing import Dict, List, Optional

from kili.domain.project import ProjectStep
from kili.domain.types import ListOrTuple


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


def convert_step_in_to_step_id_in_filter(
    asset_filter_kwargs: Dict[str, object],
    project_steps: List[ProjectStep],
    fields: Optional[ListOrTuple[str]] = None,
) -> Optional[List[str]]:
    """If a stepIn filter is given, convert it to a stepIdIn and return it."""
    step_name_in = asset_filter_kwargs.get("step_name_in")
    step_status_in = asset_filter_kwargs.get("step_status_in")
    status_in = asset_filter_kwargs.get("status_in")
    skipped = asset_filter_kwargs.get("skipped")

    if len(project_steps) != 0:
        if step_status_in is not None and status_in is not None:
            raise ValueError(
                "Filters step_status_in and status_in both given : only use filter step_status_in for this project."
            )
        if step_name_in is not None and status_in is not None:
            raise ValueError(
                "Filters step_name_in and status_in both given : use filter step_status_in instead of status_in for this project."  # pylint: disable=line-too-long
            )
        if status_in is not None:
            warnings.warn(
                "Filter status_in given : use filters step_status_in and step_name_in instead for this project.",
                stacklevel=1,
            )
        if skipped is not None:
            warnings.warn(
                "Filter skipped given : only use filter step_status_in with the SKIPPED step status instead for this project",  # pylint: disable=line-too-long
                stacklevel=1,
            )
        if fields and "status" in fields:
            warnings.warn(
                "Field status requested : request fields step and stepStatus instead for this project",
                stacklevel=1,
            )

        if (
            step_name_in is not None
            and isinstance(step_name_in, list)
            and all(isinstance(item, str) for item in step_name_in)
        ):
            return extract_step_ids_from_project_steps(
                project_steps=project_steps, step_name_in=step_name_in
            )
        return None

    if step_name_in is not None or step_status_in is not None:
        raise ValueError(
            "Filters step_name_in and/or step_status_in given : use filter status_in for this project."
        )
    return None
