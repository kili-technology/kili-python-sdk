"""Module for label parsing."""

from copy import deepcopy
from typing import Dict, Union, overload

from kili.services.label_data_parsing import json_response as json_response_module

from .types import InputType, Project


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
            print(parsed_label.jobs["JOB_0"].category.name)
            ```
        """
        super().__init__(deepcopy(label))

        self.jobs = self._initialize_jobs(json_interface=json_interface, input_type=input_type)

    @overload
    def _initialize_jobs(
        self, json_interface: Dict, input_type: InputType = "AUDIO"
    ) -> "json_response_module.ParsedJobs":
        ...

    @overload
    def _initialize_jobs(
        self, json_interface: Dict, input_type: InputType = "IMAGE"
    ) -> "json_response_module.ParsedJobs":
        ...

    @overload
    def _initialize_jobs(
        self, json_interface: Dict, input_type: InputType = "PDF"
    ) -> "json_response_module.ParsedJobs":
        ...

    @overload
    def _initialize_jobs(
        self, json_interface: Dict, input_type: InputType = "TEXT"
    ) -> "json_response_module.ParsedJobs":
        ...

    @overload
    def _initialize_jobs(
        self, json_interface: Dict, input_type: InputType = "TIME_SERIES"
    ) -> "json_response_module.ParsedJobs":
        ...

    @overload
    def _initialize_jobs(
        self, json_interface: Dict, input_type: InputType = "VIDEO"
    ) -> "json_response_module.ParsedVideoJobs":
        ...

    @overload
    def _initialize_jobs(
        self, json_interface: Dict, input_type: InputType = "VIDEO_LEGACY"
    ) -> "json_response_module.ParsedVideoJobs":
        ...

    def _initialize_jobs(
        self, json_interface: Dict, input_type: InputType
    ) -> Union["json_response_module.ParsedVideoJobs", "json_response_module.ParsedJobs"]:
        """Initializes the jobs attribute."""
        project_info = Project(inputType=input_type, jsonInterface=json_interface["jobs"])
        if "VIDEO" in input_type:
            return json_response_module.ParsedVideoJobs(
                project_info=project_info, json_response=self["jsonResponse"]
            )
        return json_response_module.ParsedJobs(
            project_info=project_info, json_response=self["jsonResponse"]
        )

    def to_dict(self) -> Dict:
        """Returns a copy of the parsed label as a dict."""
        ret = {k: deepcopy(v) for k, v in self.items() if k != "jsonResponse"}
        ret["jsonResponse"] = self.jobs.to_dict()
        return ret

    def __repr__(self) -> str:
        """Returns the representation of the object."""
        return repr(self.to_dict())

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return str(self.to_dict())
