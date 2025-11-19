"""Formatters for labels retrieved from Kili API."""

import json

from kili.domain.types import ListOrTuple


def load_label_json_fields(label: dict, fields: ListOrTuple[str]) -> dict:
    """Load json fields of a label."""
    if "jsonResponse" in fields:
        try:
            label["jsonResponse"] = json.loads(label.get("jsonResponse", "{}"))
        except json.JSONDecodeError:
            label["jsonResponse"] = {}

    return label
