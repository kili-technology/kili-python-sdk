"""Module for label parsing."""

from copy import deepcopy
from typing import Dict

from typing_extensions import Literal

from .json_response import ParsedJobs


class ParsedLabel(Dict):
    """Class that parses a label."""

    def __init__(
        self,
        label: Dict,
        json_interface: Dict,
        input_type: Literal[
            "AUDIO",
            "IMAGE",
            "PDF",
            "TEXT",
            "TIME_SERIES",
            "VIDEO",
            "VIDEO_LEGACY",
        ],
    ) -> None:
        """Class that parses a label.

        The class behaves like a dict but adds the attribute "jobs" or "frames" if the input_type is "VIDEO" or "VIDEO_LEGACY".

        The original label is not modified.

        Args:
            label: Label to parse.
            json_interface: Json interface of the project.
            input_type: Type of assets of the project.
        """
        super().__init__(deepcopy(label))

        if input_type in ["VIDEO", "VIDEO_LEGACY"]:
            self.frames = [
                ParsedJobs(frame_json_resp, json_interface)
                for frame_json_resp in self["jsonResponse"].values()
            ]
        else:
            self.jobs = ParsedJobs(self["jsonResponse"], json_interface)

    def to_dict(self) -> Dict:
        """Returns a copy of the parsed label as a dict."""
        ret = {k: deepcopy(v) for k, v in self.items() if k != "jsonResponse"}
        ret["jsonResponse"] = self.jobs.to_dict()
        return ret
