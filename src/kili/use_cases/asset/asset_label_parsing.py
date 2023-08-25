"""Parsing of the labels of an asset."""
from typing import Dict

from kili.domain.project import InputType
from kili.utils.labels.parsing import ParsedLabel, parse_labels


def parse_labels_of_asset(
    asset: Dict,
    input_type: InputType,
    project_json_interface: Dict,
) -> Dict:
    if asset.get("labels", {}).get("jsonResponse") is not None:
        asset["labels"] = parse_labels(asset["labels"], project_json_interface, input_type)
    if asset.get("latestLabel", {}).get("jsonResponse") is not None:
        asset["latestLabel"] = ParsedLabel(
            label=asset["latestLabel"],
            json_interface=project_json_interface,
            input_type=input_type,
        )
    return asset
