"""Formatters for assets retrieved from Kili API."""

import json
from typing import Dict

from kili.domain.types import ListOrTuple


def load_asset_json_fields(asset: Dict, fields: ListOrTuple[str]) -> Dict:
    """Load json fields of an asset."""
    if "jsonMetadata" in fields:
        try:
            asset["jsonMetadata"] = json.loads(asset.get("jsonMetadata", "{}"))
        except json.JSONDecodeError:
            asset["jsonMetadata"] = {}

    if "labels.jsonResponse" in fields:
        asset_labels = asset.get("labels", [])
        for label in asset_labels:
            try:
                label["jsonResponse"] = json.loads(label["jsonResponse"])
            except json.JSONDecodeError:
                label["jsonResponse"] = {}

    if "latestLabel.jsonResponse" in fields and asset.get("latestLabel") is not None:
        try:
            asset["latestLabel"]["jsonResponse"] = json.loads(asset["latestLabel"]["jsonResponse"])
        except json.JSONDecodeError:
            asset["latestLabel"]["jsonResponse"] = {}

    return asset
