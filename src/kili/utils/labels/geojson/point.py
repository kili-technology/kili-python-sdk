"""Point label utils."""

from typing import Any, Dict, List, Optional


def kili_point_to_geojson_point(point: Dict[str, float]) -> Dict[str, Any]:
    """Convert a Kili point to a geojson point.

    Args:
        point: a Kili point (vertex).

    Returns:
        A geojson point.

    !!! Example
        ```python
        >>> point = {"x": 1.0, "y": 2.0}
        >>> kili_point_to_geojson_point(point)
        {
            "type": "Point",
            "coordinates": [1.0, 2.0]
        }
        ```
    """
    return {"type": "Point", "coordinates": [point["x"], point["y"]]}


def kili_point_annotation_to_geojson_point_feature(
    point_annotation: Dict[str, Any], job_name: Optional[str] = None
) -> Dict[str, Any]:
    """Convert a Kili point annotation to a geojson point feature.

    Args:
        point_annotation: a Kili point annotation.
        job_name: the name of the job to which the annotation belongs.

    Returns:
        A geojson point feature.

    !!! Example
        ```python
        >>> point = {
            'children': {},
            'point': {'x': -79.0, 'y': -3.0},
            'categories': [{'name': 'A'}],
            'mid': 'mid_object',
            'type': 'marker'
        }
        >>> kili_point_annotation_to_geojson_point_feature(point)
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [-79.0, -3.0]},
                'id': 'mid_object',
                'properties': {
                    'kili': {
                        'categories': [{'name': 'A'}],
                        'children': {},
                        'type': 'marker'
                    }
                }
            }
        }
        ```
    """
    point = point_annotation
    assert point["type"] == "marker", f"Annotation type must be `marker`, got: {point['type']}"

    ret = {"type": "Feature", "geometry": kili_point_to_geojson_point(point["point"])}
    if "mid" in point:
        ret["id"] = point["mid"]
    ret["properties"] = {"kili": {k: v for k, v in point.items() if k not in ["point", "mid"]}}
    if job_name is not None:
        ret["properties"]["kili"]["job"] = job_name
    return ret


def geojson_point_feature_to_kili_point_annotation(
    point: Dict[str, Any],
    categories: Optional[List[Dict]] = None,
    children: Optional[Dict] = None,
    mid: Optional[str] = None,
) -> Dict[str, Any]:
    # pylint: disable=line-too-long
    """Convert a geojson point feature to a Kili point annotation.

    Args:
        point: a geojson point feature.
        categories: the categories of the annotation.
            If not provided, the categories are taken from the `kili` key of the geojson feature properties.
        children: the children of the annotation.
            If not provided, the children are taken from the `kili` key of the geojson feature properties.
        mid: the mid of the annotation.
            If not provided, the mid is taken from the `id` key of the geojson feature.

    Returns:
        A Kili point annotation.

    !!! Example
        ```python
        >>> point = {
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [-79.0, -3.0]},
            'id': 'mid_object',
            'properties': {'kili': {'categories': [{'name': 'A'}]}}
        }
        >>> geojson_point_feature_to_kili_point_annotation(point)
        {
            'children': {},
            'point': {'x': -79.0, 'y': -3.0},
            'categories': [{'name': 'A'}],
            'mid': 'mid_object',
            'type': 'marker'
        }
        ```
    """
    assert point.get("type") == "Feature", f"Feature type must be `Feature`, got: {point['type']}"
    assert (
        point["geometry"]["type"] == "Point"
    ), f"Geometry type must be `Point`, got: {point['geometry']['type']}"

    children = children or point["properties"].get("kili", {}).get("children", {})
    categories = categories or point["properties"]["kili"]["categories"]

    ret = {
        "children": children,
        "categories": categories,
        "type": "marker",
    }
    ret["point"] = {
        "x": point["geometry"]["coordinates"][0],
        "y": point["geometry"]["coordinates"][1],
    }

    if mid is not None:
        ret["mid"] = str(mid)
    elif "id" in point:
        ret["mid"] = str(point["id"])

    return ret
