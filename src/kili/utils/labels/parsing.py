"""Module for parsing labels returned by kili.labels()."""

from copy import deepcopy
from typing import Dict, Generator, Iterable, List, overload

from kili.domain.project import InputType
from kili.services.label_data_parsing import json_response as json_response_module
from kili.services.label_data_parsing.types import Project


class ParsedLabel(Dict):
    """Class that represents a parsed label."""

    def __init__(self, label: Dict, json_interface: Dict, input_type: InputType) -> None:
        # pylint: disable=line-too-long
        """Class that represents a parsed label.

        The class behaves like a dict but adds the attribute `.jobs`.

        The original input label passed to this class is not modified.

        Args:
            label: Label to parse.
            json_interface: Json interface of the project.
            input_type: Type of assets of the project.

        !!! Example
            ```python
            from kili.utils.labels.parsing import ParsedLabel

            my_label = kili.labels("project_id")[0]  # my_label is a dict

            my_parsed_label = ParsedLabel(my_label, json_interface, input_type)  # ParsedLabel object

            # Access the job "JOB_0" data through the attribute ".jobs":
            print(my_parsed_label.jobs["JOB_0"])
            ```

        !!! info
            More information about the label parsing can be found in this [tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/label_parsing/).
        """
        label_copy = deepcopy(label)
        json_response = label_copy.pop("jsonResponse", {})

        super().__init__(label_copy)

        project_info = Project(inputType=input_type, jsonInterface=json_interface["jobs"])

        self.jobs = json_response_module.ParsedJobs(
            project_info=project_info, json_response=json_response
        )

    def to_dict(self) -> Dict:
        """Return a copy of the parsed label as a dict.

        !!! Example
            ```python
            my_parsed_label = ParsedLabel(my_dict_label, json_interface, input_type)

            # Convert back to native Python dictionary
            my_label_as_dict = label.to_dict()

            assert isinstance(my_label_as_dict, dict)  # True
            ```
        """
        ret = {k: deepcopy(v) for k, v in self.items() if k != "jsonResponse"}
        ret["jsonResponse"] = self.json_response
        return ret

    def __repr__(self) -> str:
        """Return the representation of the object."""
        return repr(self.to_dict())

    def __str__(self) -> str:
        """Return the string representation of the object."""
        return str(self.to_dict())

    @property
    def json_response(self) -> Dict:
        """Returns a copy of the json response of the parsed label."""
        return self.jobs.to_dict()


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
