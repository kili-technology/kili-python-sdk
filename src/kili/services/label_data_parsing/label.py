"""Module for label parsing."""

from copy import deepcopy
from typing import Dict

from kili.core.enums import InputType
from kili.services.label_data_parsing import json_response as json_response_module

from .types import Project


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

        self.jobs = json_response_module.ParsedJobs(
            project_info=project_info, json_response=self["jsonResponse"]
        )

    def to_dict(self) -> Dict:
        """Returns a copy of the parsed label as a dict."""
        ret = {k: deepcopy(v) for k, v in self.items() if k != "jsonResponse"}
        ret["jsonResponse"] = self.jobs.to_dict()
        return ret
