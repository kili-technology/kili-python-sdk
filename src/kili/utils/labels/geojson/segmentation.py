"""Geojson segmentation utilities."""

from typing import Any, Dict, List, Optional


def kili_segmentation_to_geojson_polygon(
    bounding_poly: List[Dict[str, List[Dict[str, Any]]]],
) -> Dict[str, Any]:
    """Convert a Kili segmentation to a geojson polygon.

    Args:
        bounding_poly: a Kili segmentation bounding polygon.

    Returns:
        A geojson polygon.

    !!! Example
        ```python
        >>> bounding_poly = [
            {
                'normalizedVertices': [...]
            },
            {
                'normalizedVertices': [...]
            }
        ]
        >>> kili_segmentation_to_geojson_polygon(bounding_poly)
        {
            'type': 'Polygon',
            'coordinates': [
                [
                    ...
                ],
                [
                    ...
                ]
            ]
        }
        ```
    """
    ret = {"type": "Polygon", "coordinates": []}
    for norm_vertices_dict in bounding_poly:
        bbox = [[vertex["x"], vertex["y"]] for vertex in norm_vertices_dict["normalizedVertices"]]
        bbox.append(bbox[0])  # the first and last positions must be the same
        ret["coordinates"].append(bbox)
    return ret


def kili_segmentation_annotation_to_geojson_polygon_feature(
    segmentation_annotation: Dict[str, Any], job_name: Optional[str] = None
) -> Dict[str, Any]:
    """Convert a Kili segmentation annotation to a geojson polygon feature.

    Args:
        segmentation_annotation: a Kili segmentation annotation.
        job_name: the name of the job to which the annotation belongs.

    Returns:
        A geojson polygon feature.

    !!! Example
        ```python
        >>> segmentation = {
            'children': {},
            'boundingPoly': [
                {'normalizedVertices': [...]},
                {'normalizedVertices': [...]}
            ],
            'categories': [{'name': 'A'}],
            'mid': 'mid_object',
            'type': 'semantic'
        }
        >>> kili_segmentation_annotation_to_geojson_polygon_feature(segmentation, 'job_name')
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [
                    [
                        ...
                    ],
                    [
                        ...
                    ]
                ]
            },
            'id': 'mid_object',
            'properties': {
                'kili': {
                    'categories': [{'name': 'A'}],
                    'children': {},
                    'type': 'semantic',
                    'job': 'job_name'
                }
            }
        }
        ```
    """
    assert (
        segmentation_annotation["type"] == "semantic"
    ), f"Annotation type must be `semantic`, got: {segmentation_annotation['type']}"

    ret = {
        "type": "Feature",
        "geometry": kili_segmentation_to_geojson_polygon(segmentation_annotation["boundingPoly"]),
    }
    if "mid" in segmentation_annotation:
        ret["id"] = segmentation_annotation["mid"]
    ret["properties"] = {
        "kili": {
            k: v for k, v in segmentation_annotation.items() if k not in ["mid", "boundingPoly"]
        }
    }
    if job_name is not None:
        ret["properties"]["kili"]["job"] = job_name
    return ret


def geojson_polygon_feature_to_kili_segmentation_annotation(
    polygon: Dict[str, Any],
    categories: Optional[List[Dict]] = None,
    children: Optional[Dict] = None,
    mid: Optional[str] = None,
) -> Dict[str, Any]:
    # pylint: disable=line-too-long
    """Convert a geojson polygon feature to a Kili segmentation annotation.

    Args:
        polygon: a geojson polygon feature.
        categories: the categories of the annotation.
            If not provided, the categories are taken from the `kili` key of the geojson feature properties.
        children: the children of the annotation.
            If not provided, the children are taken from the `kili` key of the geojson feature properties.
        mid: the mid of the annotation.
            If not provided, the mid is taken from the `id` key of the geojson feature.

    Returns:
        A Kili segmentation annotation.

    !!! Example
        ```python
        >>> polygon = {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [
                    [
                        ...
                    ],
                    [
                        ...
                    ]
                ]
            },
            'id': 'mid_object',
            'properties': {
                'kili': {
                    'categories': [{'name': 'A'}],
                    'children': {},
                    'type': 'semantic',
                    'job': 'job_name'
                }
            }
        }
        >>> geojson_polygon_feature_to_kili_segmentation_annotation(polygon)
        {
            'children': {},
            'boundingPoly': [
                {'normalizedVertices': [...]},
                {'normalizedVertices': [...]}
            ],
            'categories': [{'name': 'A'}],
            'mid': 'mid_object',
            'type': 'semantic'
        }
        ```
    """
    assert (
        polygon.get("type") == "Feature"
    ), f"Feature type must be `Feature`, got: {polygon['type']}"
    assert (
        polygon["geometry"]["type"] == "Polygon"
    ), f"Geometry type must be `Polygon`, got: {polygon['geometry']['type']}"

    children = children or polygon["properties"].get("kili", {}).get("children", {})
    categories = categories or polygon["properties"]["kili"]["categories"]

    ret = {
        "children": children,
        "categories": categories,
        "type": "semantic",
    }
    coords = polygon["geometry"]["coordinates"]
    ret["boundingPoly"] = [
        {"normalizedVertices": [{"x": coord[0], "y": coord[1]} for coord in polygon[:-1]]}
        for polygon in coords
    ]

    if mid is not None:
        ret["mid"] = str(mid)
    elif "id" in polygon:
        ret["mid"] = str(polygon["id"])

    return ret
