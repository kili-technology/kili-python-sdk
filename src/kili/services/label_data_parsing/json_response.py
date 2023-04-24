# Feature is still under development and is not yet suitable for use by general users.
"""Classes for json response parsing."""

from typing import Dict, Iterator, List, Optional, Tuple

from kili.services.label_data_parsing import job_response as job_response_module

from .exceptions import FrameIndexError, JobNotExistingError
from .types import Project


class FramesList(List["job_response_module.JobPayload"]):
    """List class that allows to access the JobPayload object corresponding to a frame number."""

    def __getitem__(self, key: int) -> "job_response_module.JobPayload":
        """Returns the JobPayload object corresponding to the frame number."""
        if not 0 <= key <= len(self) - 1:
            raise FrameIndexError(frame_index=key, nb_frames=len(self))
        return super().__getitem__(key)

    @property
    def frames(self) -> "FramesList":
        """Returns the list of frames."""
        return self


class ParsedJobs:
    """Class for label json response parsing."""

    def __init__(
        self,
        project_info: Project,
        json_response: Dict,
        job_names_to_parse: Optional[List[str]] = None,
    ) -> None:
        # pylint: disable=line-too-long
        """Class for label json response parsing.

        This class will modify the input json_response.
        If you want to keep the original json_response, use deepcopy.

        Args:
            project_info: Information about the project.
            json_response: Value of the key "jsonResponse" of a label.
            job_names_to_parse: List of job names to parse. By default, parse all the jobs that are not children.
        """
        self._json_data: Dict[str, "job_response_module.JobPayload"] = {}

        json_interface = project_info["jsonInterface"]

        # all job names in the json response should be in the json interface too
        for job_name in json_response:
            if job_name not in json_interface:
                raise JobNotExistingError(job_name)

        # define the list of job names to parse
        # by default, parse all the jobs that are not children
        if job_names_to_parse is None:
            job_names_to_parse = [
                job_name
                for job_name, job_interface in json_interface.items()
                if not job_interface["isChild"]
            ]

        for job_name in job_names_to_parse:
            job_interface = json_interface[job_name]  # type: ignore
            job_response = json_response.get(job_name, {})  # the json response may be empty

            # a required parent job should have a non-empty json response
            if (
                not job_interface["isChild"]  # check if parent
                and job_interface["required"]  # check if required
                and "VIDEO" not in project_info["inputType"]  # can have empty frames
                and not job_response
            ):
                raise JobNotExistingError(job_name)

            self._json_data[job_name] = job_response_module.JobPayload(
                job_name=job_name,
                project_info=project_info,
                job_payload=job_response,
            )

    def __getitem__(self, job_name: str) -> "job_response_module.JobPayload":
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

    def __len__(self) -> int:
        """Returns the number of jobs."""
        return len(self._json_data)

    def __iter__(self) -> Iterator[str]:
        """Returns an iterator over the job names."""
        return iter(self._json_data)

    def items(self) -> Iterator[Tuple[str, "job_response_module.JobPayload"]]:
        """Returns an iterator over the job names and the corresponding JobPayload objects."""
        return iter(self._json_data.items())

    def keys(self) -> Iterator[str]:
        """Returns an iterator over the job names."""
        return iter(self._json_data.keys())

    def values(self) -> Iterator["job_response_module.JobPayload"]:
        """Returns an iterator over the JobPayload objects."""
        return iter(self._json_data.values())
