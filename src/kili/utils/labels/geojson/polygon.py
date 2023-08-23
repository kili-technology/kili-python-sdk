"""Polygon label utils."""
from typing import Any, Dict, List, Optional


def kili_polygon_to_geojson_polygon(vertices: List[Dict[str, float]]) -> Dict[str, Any]:
    """Convert a Kili polygon to a geojson polygon.

    Args:
        vertices: Kili polygon vertices.

    Returns:
        A geojson polygon.

    !!! Example
        ```python
        >>> vertices = [
            {'x': 10.42, 'y': 27.12},
            {'x': 1.53, 'y': 14.57},
            {'x': 147.45, 'y': 14.12},
            {'x': 14.23, 'y': 0.23}
        ]
        >>> kili_polygon_to_geojson_polygon(vertices)
        {
            'type': 'Polygon',
            'coordinates': [
                [
                    [10.42, 27.12],
                    [1.53, 14.57],
                    [147.45, 14.12],
                    [14.23, 0.23],
                    [10.42, 27.12]
                ]
            ]
        }
        ```
    """
    polygon = [[vertex["x"], vertex["y"]] for vertex in vertices]
    polygon.append(polygon[0])  # the first and last positions must be the same
    return {"type": "Polygon", "coordinates": [polygon]}


def kili_polygon_annotation_to_geojson_polygon_feature(
    polygon_annotation: Dict[str, Any], job_name: Optional[str] = None
) -> Dict[str, Any]:
    """Convert a Kili polygon annotation to a geojson polygon feature.

    Args:
        polygon_annotation: a Kili polygon annotation.
        job_name: the name of the job to which the annotation belongs.

    Returns:
        A geojson polygon feature.

    !!! Example
        ```python
        >>> polygon = {
            'children': {},
            'boundingPoly': [{'normalizedVertices': [{'x': -79.0, 'y': -3.0}]}],
            'categories': [{'name': 'A'}],
            'mid': 'mid_object',
            'type': 'polygon'
        }
        >>> kili_polygon_annotation_to_geojson_polygon_feature(polygon, 'job_name')
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [[[-79.0, -3.0], [-79.0, -3.0]]]},
                'id': 'mid_object',
                'properties': {
                    'kili': {
                        'categories': [{'name': 'A'}],
                        'children': {},
                        'type': 'polygon',
                        'job': 'job_name'
                    }
                }
            }
        }
        ```
    """
    polygon = polygon_annotation
    assert (
        polygon["type"] == "polygon"
    ), f"Annotation type must be `polygon`, got: {polygon['type']}"

    ret = {
        "type": "Feature",
        "geometry": kili_polygon_to_geojson_polygon(
            polygon["boundingPoly"][0]["normalizedVertices"]
        ),
    }
    if "mid" in polygon:
        ret["id"] = polygon["mid"]
    ret["properties"] = {
        "kili": {k: v for k, v in polygon.items() if k not in ["boundingPoly", "mid"]}
    }
    if job_name is not None:
        ret["properties"]["kili"]["job"] = job_name
    return ret


def geojson_polygon_feature_to_kili_polygon_annotation(
    polygon: Dict[str, Any],
    categories: Optional[List[Dict]] = None,
    children: Optional[Dict] = None,
    mid: Optional[str] = None,
) -> Dict[str, Any]:
    # pylint: disable=line-too-long
    """Convert a geojson polygon feature to a Kili polygon annotation.

    Args:
        polygon: a geojson polygon feature.
        categories: the categories of the annotation.
            If not provided, the categories are taken from the `kili` key of the geojson feature properties.
        children: the children of the annotation.
            If not provided, the children are taken from the `kili` key of the geojson feature properties.
        mid: the mid of the annotation.
            If not provided, the mid is taken from the `id` key of the geojson feature.


    Returns:
        A Kili polygon annotation.

    !!! Example
        ```python
        >>> polygon = {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [[[-79.0, -3.0], [-79.0, -3.0]]]},
            },
            'id': 'mid_object',
            'properties': {
                'kili': {
                    'categories': [{'name': 'A'}],
                    'children': {},
                    'type': 'polygon',
                    'job': 'job_name'
                }
            }
        }
        >>> geojson_polygon_feature_to_kili_polygon_annotation(polygon)
        {
            'children': {},
            'boundingPoly': [{'normalizedVertices': [{'x': -79.0, 'y': -3.0}]}],
            'categories': [{'name': 'A'}],
            'mid': 'mid_object',
            'type': 'polygon'
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
        "type": "polygon",
    }
    coords = polygon["geometry"]["coordinates"][0]
    normalized_vertices = [{"x": coord[0], "y": coord[1]} for coord in coords[:-1]]
    ret["boundingPoly"] = [{"normalizedVertices": normalized_vertices}]

    if mid is not None:
        ret["mid"] = str(mid)
    elif "id" in polygon:
        ret["mid"] = str(polygon["id"])

    return ret
