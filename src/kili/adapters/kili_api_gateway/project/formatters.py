"""Formatters for projects retrieved from Kili API."""

import json
from typing import Dict

from kili.domain.types import ListOrTuple

PROJECT_JSON_FIELDS = ("jsonInterface",)


def load_project_json_fields(project: Dict, fields: ListOrTuple[str]) -> Dict:
    """Load json fields of a project."""
    if "jsonInterface" in fields and isinstance(project.get("jsonInterface"), str):
        try:
            project["jsonInterface"] = json.loads(project["jsonInterface"])
        except json.JSONDecodeError:
            project["jsonInterface"] = {}
    return project
