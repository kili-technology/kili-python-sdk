# Feature is still under development and is not yet suitable for use by general users.
"""Classes for json response parsing."""

from typing import Dict

from .exceptions import JobNotExistingError
from .job_response import JobPayload
from .types import Project


class ParsedJobs:
    """Class for label json response parsing."""

    def __init__(self, project_info: Project, json_response: Dict) -> None:
        """Class for label json response parsing.

        Args:
            project_info: Information about the project.
            json_response: Value of the key "jsonResponse" of a label.
        """
        self._json_data: Dict[str, JobPayload] = {}

        json_interface = project_info["jsonInterface"]

        for job_name, job_interface in json_interface.items():
            job_response = json_response.get(job_name, {})

            if job_interface.get("isChild"):
                continue

            if job_interface["required"] and not job_response:
                raise JobNotExistingError(job_name)

            self._json_data[job_name] = JobPayload(
                job_name=job_name,
                project_info=project_info,
                job_payload=job_response,
            )

        # check that the job names in the json response are in the json interface
        for job_name in json_response:
            if job_name not in json_interface:
                raise JobNotExistingError(job_name)

    def __getitem__(self, job_name: str) -> JobPayload:
        """Returns the JobPayload object corresponding to the job name."""
        if job_name not in self._json_data:
            raise JobNotExistingError(job_name)
        return self._json_data[job_name]

    def to_dict(self) -> Dict:
        """Returns the parsed json response as a dict."""
        ret = {job_name: job_payload.to_dict() for job_name, job_payload in self._json_data.items()}
        ret = {k: v for k, v in ret.items() if v}  # remove empty json responses
        return ret

    def __repr__(self) -> str:
        """Returns the representation of the object."""
        return repr(self.to_dict())

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return str(self.to_dict())
