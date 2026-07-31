"""Export of geospatial projects labeled in the image's own sensor pixel grid.

Those projects store annotations normalized against the image, like an image asset, so
the export unnormalizes them with its dimensions. GeoJSON is not offered.
"""

import logging
from collections.abc import Mapping
from typing import Any, Optional

logger = logging.getLogger(__name__)

PIXEL_LABELING_CRS_CODE = "PIXEL"

_VERTEX_CONTAINERS = ("boundingPoly", "polyline", "point")


def is_pixel_labeling_project(project: Mapping[str, Any]) -> bool:
    """Whether the project labels in the image's own pixel grid."""
    geospatial_settings = project.get("geospatialSettings") or {}
    return geospatial_settings.get("labelingCRSCode") == PIXEL_LABELING_CRS_CODE


def get_asset_pixel_dimensions(asset: dict) -> Optional[tuple[int, int]]:
    """Reads the image dimensions recorded at import time."""
    layers: list[dict] = asset.get("geospatialExportMetadata") or []
    for layer in layers:
        width, height = layer.get("width"), layer.get("height")
        if width and height:
            return int(width), int(height)
    return None


def _scale_vertex(vertex: dict, width: int, height: int) -> dict:
    return {**vertex, "x": vertex["x"] * width, "y": vertex["y"] * height}


def _scale_annotation(annotation: dict, width: int, height: int) -> None:
    for key in _VERTEX_CONTAINERS:
        value = annotation.get(key)
        if value is None:
            continue

        if key == "point":
            annotation[key] = _scale_vertex(value, width, height)
        elif key == "boundingPoly":
            annotation[key] = [
                {
                    **norm_vertices,
                    "normalizedVertices": [
                        _scale_vertex(vertex, width, height)
                        for vertex in norm_vertices["normalizedVertices"]
                    ],
                }
                for norm_vertices in value
            ]
        else:
            annotation[key] = [_scale_vertex(vertex, width, height) for vertex in value]


def _scale_json_response(json_response: dict, width: int, height: int) -> None:
    for job_response in json_response.values():
        if not isinstance(job_response, dict):
            continue
        for annotation in job_response.get("annotations", []):
            _scale_annotation(annotation, width, height)


def convert_to_pixel_coords(asset: dict) -> dict:
    """Turns the normalized coordinates of an asset's labels into image pixels."""
    dimensions = get_asset_pixel_dimensions(asset)
    if dimensions is None:
        logger.warning(
            "Asset %s has no recorded image dimensions: its labels stay normalized",
            asset.get("externalId") or asset.get("id"),
        )
        return asset

    width, height = dimensions

    labels = []
    if asset.get("latestLabel"):
        labels.append(asset["latestLabel"])
    labels.extend(asset.get("labels") or [])
    labels.extend(label for label in (asset.get("latestLabels") or []) if label)

    for label in labels:
        json_response = label.get("jsonResponse")
        if json_response:
            _scale_json_response(json_response, width, height)

    return asset
