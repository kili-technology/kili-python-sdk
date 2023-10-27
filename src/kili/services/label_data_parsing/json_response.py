"""Classes for json response parsing."""

from typing import Dict, Iterator, List, Optional, Tuple, cast

from kili.services.label_data_parsing import job_response as job_response_module

from .exceptions import FrameIndexError, JobNotExistingError
from .types import Project


# pylint: disable=too-few-public-methods
class _ParsedVideoJobs:
    def __init__(
        self,
        project_info: Project,
        json_response: Dict,
        job_names_to_parse: Optional[List[str]] = None,
    ) -> None:
        self._json_data: Dict[str, "FramesList"] = {}

        self._nb_frames = len(json_response)

        json_interface = project_info["jsonInterface"]

        # all job names in the json response should be in the json interface too
        for frame_response in json_response.values():
            for job_name in frame_response:
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

        for current_job_name in job_names_to_parse:
            frames_list_for_job = []
            for _, frame_json_response in sorted(
                json_response.items(),
                key=lambda item: int(item[0]),  # sort by frame number
            ):
                job_response = frame_json_response.get(current_job_name, {})
                job_payload = job_response_module.JobPayload(
                    job_name=current_job_name,
                    project_info=project_info,
                    job_payload=job_response,
                )
                frames_list_for_job.append(job_payload)

            assert len(frames_list_for_job) == self._nb_frames, (
                f"len(frames_list_for_job) = {len(frames_list_for_job)} != {self._nb_frames} ="
                " self._nb_frames"
            )
            self._json_data[current_job_name] = FramesList(frames_list_for_job)

    def to_dict(self) -> Dict[str, Dict]:
        """Returns a copy of the parsed label as a dict."""
        ret = {str(frame_id): {} for frame_id in range(self._nb_frames)}
        for job_name, frames_list in self._json_data.items():
            for frame_id, job_payload in enumerate(frames_list):
                job_payload_dict = job_payload.to_dict()
                if job_payload_dict:
                    ret[str(frame_id)][job_name] = job_payload_dict
        return ret


# pylint: disable=too-few-public-methods
class _ParsedJobs:
    def __init__(
        self,
        project_info: Project,
        json_response: Dict,
        job_names_to_parse: Optional[List[str]] = None,
    ) -> None:
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
            job_response = json_response.get(job_name, {})  # the json response can be empty
            self._json_data[job_name] = job_response_module.JobPayload(
                job_name=job_name,
                project_info=project_info,
                job_payload=job_response,
            )

    def to_dict(self) -> Dict[str, Dict]:
        """Returns the parsed json response as a dict."""
        ret = {job_name: job_payload.to_dict() for job_name, job_payload in self._json_data.items()}
        return {k: v for k, v in ret.items() if v}  # remove empty json responses


def _is_video_response(project_info: Project, json_response: Dict) -> bool:
    """Returns True if the json response is a video job, False otherwise."""
    if "VIDEO" not in project_info["inputType"]:
        return False

    if not all(frame_id.isdigit() for frame_id in json_response):
        return False

    for frame_response in json_response.values():
        if len(frame_response) == 0:
            continue

        for job_name in frame_response:
            if not (isinstance(job_name, str) and job_name in project_info["jsonInterface"]):
                return False

    return True


class ParsedJobs(_ParsedJobs, _ParsedVideoJobs):
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
        self._is_video_response = _is_video_response(project_info, json_response)

        if self._is_video_response:
            _ParsedVideoJobs.__init__(
                self,
                project_info=project_info,
                json_response=json_response,
                job_names_to_parse=job_names_to_parse,
            )
        else:
            _ParsedJobs.__init__(
                self,
                project_info=project_info,
                json_response=json_response,
                job_names_to_parse=job_names_to_parse,
            )

    def to_dict(self) -> Dict[str, Dict]:
        """Returns the parsed json response as a dict."""
        if self._is_video_response:
            return _ParsedVideoJobs.to_dict(self)
        return _ParsedJobs.to_dict(self)

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

    def items(self) -> Iterator[Tuple[str, "JobPayload"]]:
        """Returns an iterator over the job names and the corresponding objects."""
        return cast(Iterator[Tuple[str, "JobPayload"]], iter(self._json_data.items()))

    def keys(self) -> Iterator[str]:
        """Returns an iterator over the job names."""
        return iter(self._json_data.keys())

    def values(self) -> Iterator["JobPayload"]:
        """Returns an iterator over the objects."""
        return cast(Iterator["JobPayload"], iter(self._json_data.values()))

    def __getitem__(self, job_name: str) -> "JobPayload":
        """Returns the object corresponding to the job name.

        For a video job, the returned object is a FramesList.

        Otherwise, the returned object is a JobPayload.
        """
        if job_name not in self._json_data:
            raise JobNotExistingError(job_name)
        return cast("JobPayload", self._json_data[job_name])


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


class JobPayload(FramesList, job_response_module.JobPayload):
    # pylint: disable=line-too-long
    """JobPayload class.

    It is the value of the parsed job response of a job `job_name`: `label.jobs["job_name"]`.

    If the job is a video job, it can be used to access the job response of a frame `frame_number`: `label.jobs["job_name"].frames[frame_number]`.
    """

    # Class only used for return type hints.
    # It should not be instantiated.
    # It inherits from both FramesList and JobResponseModule.JobPayload to expose the methods
    # and properties of both classes.
