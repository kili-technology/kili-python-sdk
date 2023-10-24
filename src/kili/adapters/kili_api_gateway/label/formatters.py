"""Formatters for labels retrieved from Kili API."""

import json
from typing import Dict

from kili.domain.types import ListOrTuple


def load_label_json_fields(label: Dict, fields: ListOrTuple[str]) -> Dict:
    """Load json fields of a label."""
    if "jsonResponse" in fields:
        label["jsonResponse"] = json.loads(label.get("jsonResponse", "{}"))

    return label
