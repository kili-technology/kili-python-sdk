# Feature is still under development and is not yet suitable for use by general users.
"""Classes for json response parsing."""

from typing import Dict

from .exceptions import JobNotExistingError
from .job_response import JobPayload


class ParsedJobs(Dict):
    """Class for label json response parsing."""

    def __init__(self, json_response: Dict, json_interface: Dict):
        """Class for label json response parsing.

        Args:
            json_response: Value of the key "jsonResponse" of a label.
            json_interface: Json interface of the project.
        """
        super().__init__()

        self.json_response = json_response
        self.json_interface = json_interface

        for job_name, job_interface in json_interface["jobs"].items():
            job_response = json_response.get(job_name, {})

            if job_interface["required"] and not job_response:
                raise JobNotExistingError(job_name)

            self[job_name] = JobPayload(
                job_name=job_name,
                job_interface=job_interface,
                job_payload=job_response,
            )

        # check that the job names in the json response are in the json interface
        for job_name in json_response:
            if job_name not in json_interface["jobs"]:
                raise JobNotExistingError(job_name)

    def __getitem__(self, job_name: str) -> JobPayload:
        """Returns the JobPayload object corresponding to the job name."""
        if job_name not in self:
            raise JobNotExistingError(job_name)
        return super().__getitem__(job_name)
