"""Module for label parsing."""

from copy import deepcopy
from typing import Dict

from .json_response import ParsedJobs


class ParsedLabel(Dict):
    """Class that parses a label."""

    def __init__(self, label: Dict, json_interface: Dict) -> None:
        """Class that parses a label.

        The class behaves like a dict but adds the attribute "jobs".

        Args:
            label: Label to parse.
            json_interface: Json interface of the project.
        """
        super().__init__(label)  # copy the input label dict

        self.jobs = ParsedJobs(self["jsonResponse"], json_interface)

    def to_dict(self) -> Dict:
        """Returns a copy of the parsed label as a dict."""
        ret = {k: deepcopy(v) for k, v in self.items() if k != "jsonResponse"}
        ret["jsonResponse"] = self.jobs.to_dict()
        return ret
