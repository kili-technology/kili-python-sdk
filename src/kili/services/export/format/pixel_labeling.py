"""Export of geospatial projects labeled in the image's own sensor pixel grid.

Those projects store annotations normalized against the image, like an image asset, so
the export adds the pixel coordinates beside the normalized ones, under the same keys an
image project uses: `vertices` next to `boundingPoly[].normalizedVertices`, and
`pointPixels` / `polylinePixels` next to `point` / `polyline`. The normalized values are
left untouched — a consumer that reads them must keep reading fractions.

GeoJSON is not offered.
"""

import logging
from collections.abc import Mapping
from typing import Any, Optional

logger = logging.getLogger(__name__)

PIXEL_LABELING_CRS_CODE = "PIXEL"


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
    """Adds the pixel coordinates beside the normalized ones, in place."""
    # Bounding boxes, polygons, segmentation: `vertices` beside `normalizedVertices`.
    bounding_poly = annotation.get("boundingPoly")
    if bounding_poly is not None:
        annotation["boundingPoly"] = [
            {
                **norm_vertices,
                "vertices": [
                    _scale_vertex(vertex, width, height)
                    for vertex in norm_vertices["normalizedVertices"]
                ],
            }
            for norm_vertices in bounding_poly
        ]

    point = annotation.get("point")
    if point is not None:
        annotation["pointPixels"] = _scale_vertex(point, width, height)

    polyline = annotation.get("polyline")
    if polyline is not None:
        annotation["polylinePixels"] = [_scale_vertex(vertex, width, height) for vertex in polyline]


def _scale_json_response(json_response: dict, width: int, height: int) -> None:
    for job_response in json_response.values():
        if not isinstance(job_response, dict):
            continue
        for annotation in job_response.get("annotations", []):
            _scale_annotation(annotation, width, height)


def convert_to_pixel_coords(asset: dict) -> dict:
    """Adds the image pixel coordinates of an asset's labels, beside the normalized ones."""
    dimensions = get_asset_pixel_dimensions(asset)
    if dimensions is None:
        logger.warning(
            "Asset %s has no recorded image dimensions: its labels carry no pixel coordinates",
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
