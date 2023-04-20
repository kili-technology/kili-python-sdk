"""Module for label parsing."""

from copy import deepcopy
from typing import Dict, List

from kili.core.enums import InputType
from kili.services.label_data_parsing import json_response as json_response_module

from .exceptions import FrameIndexError
from .types import Project


class FramesList(List["json_response_module.ParsedJobs"]):
    """List class that allows to access the ParsedJobs object corresponding to a frame number."""

    def __getitem__(self, key: int) -> "json_response_module.ParsedJobs":
        """Returns the ParsedJobs object corresponding to the frame number."""
        if not 0 <= key <= len(self) - 1:
            raise FrameIndexError(frame_index=key, nb_frames=len(self))
        return super().__getitem__(key)


class ParsedLabel(Dict):
    """Class that parses a label."""

    def __init__(self, label: Dict, json_interface: Dict, input_type: InputType) -> None:
        """Class that parses a label.

        The class behaves like a dict but adds the attribute "jobs".

        The original label is not modified.

        Args:
            label: Label to parse.
            json_interface: Json interface of the project.
            input_type: Type of assets of the project.

        !!! Example
            ```python
            label = kili.labels(...)[0]
            parsed_label = ParsedLabel(label, json_interface, input_type)
            print(parsed_label.jobs["JOB_0"].category.name)  # "A"
            ```
        """
        super().__init__(deepcopy(label))

        project_info = Project(inputType=input_type, jsonInterface=json_interface["jobs"])

        if "VIDEO" in input_type:
            self.frames = FramesList(
                json_response_module.ParsedJobs(
                    project_info=project_info, json_response=frame_json_resp
                )
                for _, frame_json_resp in sorted(
                    self["jsonResponse"].items(), key=lambda item: int(item[0])
                )
            )
        else:
            self.jobs = json_response_module.ParsedJobs(
                project_info=project_info, json_response=self["jsonResponse"]
            )

    def to_dict(self) -> Dict:
        """Returns a copy of the parsed label as a dict."""
        ret = {k: deepcopy(v) for k, v in self.items() if k != "jsonResponse"}
        if hasattr(self, "frames"):
            ret["jsonResponse"] = {str(k): v.to_dict() for k, v in enumerate(self.frames)}
        else:
            ret["jsonResponse"] = self.jobs.to_dict()
        return ret

    def __repr__(self) -> str:
        """Returns the representation of the object."""
        return repr(self.to_dict())

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return str(self.to_dict())
