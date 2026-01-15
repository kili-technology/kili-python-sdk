"""Formatters for labels retrieved from Kili API."""

import json

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.helpers.http_json import load_json_from_link
from kili.core.helpers import is_url
from kili.domain.types import ListOrTuple


def load_label_json_fields(label: dict, fields: ListOrTuple[str], http_client: HttpClient) -> dict:
    """Load json fields of a label."""
    if "jsonResponse" in fields:
        json_response_url = label.get("jsonResponseUrl")
        if json_response_url and is_url(json_response_url):
            label["jsonResponse"] = load_json_from_link(json_response_url, http_client)
            del label["jsonResponseUrl"]
        else:
            json_response_value = label.get("jsonResponse", "{}")
            try:
                label["jsonResponse"] = json.loads(json_response_value)
            except json.JSONDecodeError:
                label["jsonResponse"] = {}

    return label
