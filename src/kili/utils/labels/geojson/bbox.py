"""Bounding box conversion functions between Kili and geojson formats."""

from typing import Any, Dict, List, Optional


def kili_bbox_to_geojson_polygon(vertices: List[Dict[str, float]]) -> Dict[str, Any]:
    """Convert a Kili bounding box to a geojson polygon.

    Args:
        vertices: Kili bounding polygon vertices.

    Returns:
        A geojson polygon.

    !!! Example
        ```python
        >>> vertices = [
            {'x': 12.0, 'y': 3.0},
            {'x': 12.0, 'y': 4.0},
            {'x': 13.0, 'y': 4.0},
            {'x': 13.0, 'y': 3.0}
        ]
        >>> kili_bbox_to_geojson_polygon(vertices)
        {
            'type': 'Polygon',
            'coordinates': [
                [
                    [12.0, 3.0],
                    [12.0, 4.0],
                    [13.0, 4.0],
                    [13.0, 3.0],
                    [12.0, 3.0]
                ]
            ]
        }
        ```
    """
    vertex_name_to_value = {}
    for vertex, point_name in zip(
        vertices, ("bottom_left", "top_left", "top_right", "bottom_right")
    ):
        vertex_name_to_value[point_name] = vertex

    ret = {"type": "Polygon", "coordinates": []}
    ret["coordinates"] = [
        [
            [vertex_name_to_value["bottom_left"]["x"], vertex_name_to_value["bottom_left"]["y"]],
            [vertex_name_to_value["bottom_right"]["x"], vertex_name_to_value["bottom_right"]["y"]],
            [vertex_name_to_value["top_right"]["x"], vertex_name_to_value["top_right"]["y"]],
            [vertex_name_to_value["top_left"]["x"], vertex_name_to_value["top_left"]["y"]],
            [vertex_name_to_value["bottom_left"]["x"], vertex_name_to_value["bottom_left"]["y"]],
        ]
    ]

    return ret


def kili_bbox_annotation_to_geojson_polygon_feature(
    bbox_annotation: Dict[str, Any], job_name: Optional[str] = None
) -> Dict[str, Any]:
    """Convert a Kili bounding box annotation to a geojson polygon feature.

    Args:
        bbox_annotation: a Kili bounding box annotation.
        job_name: the name of the job to which the annotation belongs.

    Returns:
        A geojson polygon feature.

    !!! Example
        ```python
        >>> bbox = {
            'children': {},
            'boundingPoly': [
                    {
                        'normalizedVertices': [
                            {'x': -12.6, 'y': 12.87},
                            {'x': -42.6, 'y': 22.17},
                            {'x': -17.6, 'y': -22.4},
                            {'x': 2.6, 'y': -1.87}
                        ]
                    }
                ],
            'categories': [{'name': 'A'}],
            'mid': 'mid_object',
            'type': 'rectangle'
        }
        >>> kili_bbox_annotation_to_geojson_polygon_feature(bbox, 'job_name')
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [
                    [
                        [-12.6, 12.87],
                        [-42.6, 22.17],
                        [-17.6, -22.4],
                        [2.6, -1.87],
                        [-12.6, 12.87]
                    ]
                ]
            },
            'id': 'mid_object',
            'properties': {
                'kili': {
                    'categories': [{'name': 'A'}],
                    'children': {},
                    'type': 'rectangle',
                    'job': 'job_name'
                }
            }
        }
        ```
    """
    bbox = bbox_annotation
    assert bbox["type"] == "rectangle", f"Annotation type must be `rectangle`, got: {bbox['type']}"

    ret = {
        "type": "Feature",
        "geometry": kili_bbox_to_geojson_polygon(bbox["boundingPoly"][0]["normalizedVertices"]),
    }
    if "mid" in bbox:
        ret["id"] = bbox["mid"]
    ret["properties"] = {
        "kili": {k: v for k, v in bbox.items() if k not in ["boundingPoly", "mid"]}
    }
    if job_name is not None:
        ret["properties"]["kili"]["job"] = job_name
    return ret


def geojson_polygon_feature_to_kili_bbox_annotation(
    polygon: Dict[str, Any],
    categories: Optional[List[Dict]] = None,
    children: Optional[Dict] = None,
    mid: Optional[str] = None,
) -> Dict[str, Any]:
    # pylint: disable=line-too-long
    """Convert a geojson polygon feature to a Kili bounding box annotation.

    Args:
        polygon: a geojson polygon feature.
        categories: the categories of the annotation.
            If not provided, the categories are taken from the `kili` key of the geojson feature properties.
        children: the children of the annotation.
            If not provided, the children are taken from the `kili` key of the geojson feature properties.
        mid: the mid of the annotation.
            If not provided, the mid is taken from the `id` key of the geojson feature.

    Returns:
        A Kili bounding box annotation.

    !!! Example
        ```python
        >>> polygon = {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [
                    [
                        [-12.6, 12.87],
                        [-42.6, 22.17],
                        [-17.6, -22.4],
                        [2.6, -1.87],
                        [-12.6, 12.87]
                    ]
                ]
            },
            'id': 'mid_object',
            'properties': {
                'kili': {
                    'categories': [{'name': 'A'}],
                    'children': {},
                    'type': 'rectangle',
                    'job': 'job_name'
                }
            }
        }
        >>> geojson_polygon_feature_to_kili_bbox_annotation(polygon)
        {
            'children': {},
            'boundingPoly': [
                    {
                        'normalizedVertices': [
                            {'x': -12.6, 'y': 12.87},
                            {'x': -42.6, 'y': 22.17},
                            {'x': -17.6, 'y': -22.4},
                            {'x': 2.6, 'y': -1.87}
                        ]
                    }
                ],
            'categories': [{'name': 'A'}],
            'mid': 'mid_object',
            'type': 'rectangle'
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
        "type": "rectangle",
    }
    # geojson polygon has one more point than kili bounding box
    coords = polygon["geometry"]["coordinates"][0]
    normalized_vertices = [
        {"x": coords[0][0], "y": coords[0][1]},
        {"x": coords[3][0], "y": coords[3][1]},
        {"x": coords[2][0], "y": coords[2][1]},
        {"x": coords[1][0], "y": coords[1][1]},
    ]
    ret["boundingPoly"] = [{"normalizedVertices": normalized_vertices}]

    if mid is not None:
        ret["mid"] = mid
    elif "id" in polygon:
        ret["mid"] = polygon["id"]

    return ret
