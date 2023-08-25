"""Parsing of the labels of an asset."""
from typing import Dict

from kili.services.label_data_parsing.types import Project as LabelParsingProject
from kili.utils.labels.parsing import ParsedLabel, parse_labels


def parse_labels_of_asset(asset: Dict, project: LabelParsingProject) -> Dict:
    """Parse the labels of an asset queried to Kili."""
    if asset.get("labels", {}).get("jsonResponse") is not None:
        asset["labels"] = parse_labels(
            asset["labels"], project["jsonInterface"], project["inputType"]
        )
    if asset.get("latestLabel", {}).get("jsonResponse") is not None:
        asset["latestLabel"] = ParsedLabel(
            label=asset["latestLabel"],
            json_interface=project["jsonInterface"],
            input_type=project["inputType"],
        )
    return asset
