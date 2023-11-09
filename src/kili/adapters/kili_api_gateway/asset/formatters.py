"""Formatters for assets retrieved from Kili API."""

import json
from typing import Dict

from kili.domain.types import ListOrTuple


def load_asset_json_fields(asset: Dict, fields: ListOrTuple[str]) -> Dict:
    """Load json fields of an asset."""
    if "jsonMetadata" in fields:
        asset["jsonMetadata"] = json.loads(asset.get("jsonMetadata", "{}"))

    if "labels.jsonResponse" in fields:
        asset_labels = asset.get("labels", [])
        for label in asset_labels:
            label["jsonResponse"] = json.loads(label["jsonResponse"])

    if "latestLabel.jsonResponse" in fields and asset.get("latestLabel") is not None:
        asset["latestLabel"]["jsonResponse"] = json.loads(asset["latestLabel"]["jsonResponse"])

    return asset
