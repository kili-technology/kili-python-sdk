"""Module for label parsing."""

from typing import Dict

from .json_response import ParsedJobs


class ParsedLabel(Dict):
    """Class that parses a label."""

    def __init__(self, label: Dict, json_interface: Dict, inplace: bool = False):
        """Class that parses a label.

        The class behaves like a dict but adds the key "jobs".

        Args:
            label: Label to parse.
            json_interface: Json interface of the project.
            inplace: If True, the input label is modified inplace.
        """
        if inplace:
            self.update(label)
        else:
            super().__init__(label)  # copy the input label dict

        self.jobs = ParsedJobs(label["jsonResponse"], json_interface)
