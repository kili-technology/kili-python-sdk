"""Formatters for assets retrieved from Kili API."""

import json
from typing import Dict

from kili.adapters.http_client import HttpClient
from kili.core.helpers import get_response_json, is_url, log_raise_for_status
from kili.domain.types import ListOrTuple


def load_json_from_link(link: str, http_client: HttpClient) -> Dict:
    """Load json from link."""
    if link == "" or not is_url(link):
        return {}

    response = http_client.get(link, timeout=30)
    log_raise_for_status(response)
    return get_response_json(response)


def load_asset_json_fields(asset: Dict, fields: ListOrTuple[str], http_client: HttpClient) -> Dict:
    """Load json fields of an asset."""
    if "jsonMetadata" in fields:
        try:
            asset["jsonMetadata"] = json.loads(asset.get("jsonMetadata", "{}"))
        except json.JSONDecodeError:
            asset["jsonMetadata"] = {}

    if "ocrMetadata" in fields and asset.get("ocrMetadata") is not None:
        asset["ocrMetadata"] = load_json_from_link(asset.get("ocrMetadata", ""), http_client)

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
