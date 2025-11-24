"""Set of utils for label data parsing service module."""

from typing import Union

from kili_formats.types import Job


def get_children_job_names(json_interface: dict, job_interface: Union[Job, dict]) -> list[str]:
    """Returns the list of children job names of a parent job interface."""
    children_job_names = []

    for key, value in job_interface.items():
        if (
            key == "children"
            and isinstance(value, list)
            and all(job_name in json_interface for job_name in value)
            and all(json_interface[job_name]["isChild"] for job_name in value)
        ):
            children_job_names.extend(value)

        elif isinstance(value, dict):
            children_job_names.extend(
                get_children_job_names(json_interface=json_interface, job_interface=value)
            )

        # pose estimation json interface
        elif key == "points" and isinstance(value, list):
            for point in value:
                children_job_names.extend(
                    get_children_job_names(json_interface=json_interface, job_interface=point)
                )

    return children_job_names
