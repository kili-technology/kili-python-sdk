"""Module for parsing labels returned by kili.labels()."""

from copy import deepcopy
from typing import Dict, Generator, Iterable, List, overload

from kili.services.label_data_parsing import json_response as json_response_module
from kili.services.label_data_parsing.types import InputType, Project


class ParsedLabel(Dict):
    """Class that represents a parsed label."""

    def __init__(self, label: Dict, json_interface: Dict, input_type: InputType) -> None:
        """Class that represents a parsed label.

        The class behaves like a dict but adds the attribute "jobs".

        The original input label passed to this class is not modified.

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

        project_info = Project(inputType=input_type, jsonInterface=json_interface["jobs"])

        self.jobs = json_response_module.ParsedJobs(
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


@overload
def parse_labels(
    labels: List[Dict], json_interface: Dict, input_type: InputType
) -> List[ParsedLabel]:
    ...


@overload
def parse_labels(
    labels: Generator[Dict, None, None], json_interface: Dict, input_type: InputType
) -> Generator[ParsedLabel, None, None]:
    ...


def parse_labels(
    labels: Iterable[Dict], json_interface: Dict, input_type: InputType
) -> Iterable[ParsedLabel]:
    """Parse labels returned by kili.labels().

    Args:
        labels: List or generator of labels from kili.labels().
        json_interface: Json interface of the project.
        input_type: Type of assets of the project.

    Returns:
        Parsed labels.
    """
    gen = (
        ParsedLabel(label=label, json_interface=json_interface, input_type=input_type)
        for label in labels
    )
    return gen if isinstance(labels, Generator) else list(gen)
