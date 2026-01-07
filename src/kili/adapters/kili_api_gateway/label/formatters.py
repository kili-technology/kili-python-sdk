"""Formatters for labels retrieved from Kili API."""

import json

from kili.adapters.http_client import HttpClient
from kili.core.helpers import is_url
from kili.domain.types import ListOrTuple


def load_json_from_link(link: str, http_client: HttpClient) -> dict:
    """Load json from link."""
    if link == "" or not is_url(link):
        return {}

    response = http_client.get(link, timeout=30)
    response.raise_for_status()
    return response.json()


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
