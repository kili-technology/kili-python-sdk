"""Set of utils to work with labels."""

from typing import Dict, Generator, Iterable, List, overload

from typing_extensions import Literal

from ...services.json_response.label import ParsedLabel


@overload
def parse_labels(
    labels: Iterable[Dict], json_interface: Dict, as_generator: Literal[False] = False
) -> List[ParsedLabel]:
    ...


@overload
def parse_labels(
    labels: Iterable[Dict], json_interface: Dict, as_generator: Literal[True]
) -> Generator[ParsedLabel, None, None]:
    ...


def parse_labels(
    labels: Iterable[Dict], json_interface: Dict, as_generator: bool = False
) -> Iterable[ParsedLabel]:
    """Parse labels returned by kili.labels().

    Args:
        labels: List of labels from kili.labels().
        json_interface: Json interface of the project.
        as_generator: If True, returns a generator instead of a list.

    Returns:
        Parsed labels.
    """
    gen = (ParsedLabel(label=label, json_interface=json_interface) for label in labels)
    if as_generator:
        return gen
    return list(gen)
