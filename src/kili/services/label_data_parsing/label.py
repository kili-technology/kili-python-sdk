"""Module for label parsing."""

from typing import Dict

from .json_response import ParsedJobs


class ParsedLabel(Dict):
    """Class that parses a label."""

    def __init__(self, label: Dict, json_interface: Dict):
        """Class that parses a label.

        The class behaves like a dict but adds the key "jobs".

        Args:
            label: Label to parse.
            json_interface: Json interface of the project.
        """
        super().__init__(label)  # copy the input label dict

        self.jobs = ParsedJobs(label["jsonResponse"], json_interface)
