"""Module for parsing labels returned by kili.labels()."""

from typing import Dict, Generator, Iterable, List, overload

from kili.core.enums import InputType

from ...services.label_data_parsing.label import ParsedLabel


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
