"""Formatters for projects retrieved from Kili API."""

import json

from kili.domain.types import ListOrTuple

PROJECT_JSON_FIELDS = ("jsonInterface",)


def load_project_json_fields(project: dict, fields: ListOrTuple[str]) -> dict:
    """Load json fields of a project."""
    if "jsonInterface" in fields and isinstance(project.get("jsonInterface"), str):
        try:
            project["jsonInterface"] = json.loads(project["jsonInterface"])
        except json.JSONDecodeError:
            project["jsonInterface"] = {}
    return project
