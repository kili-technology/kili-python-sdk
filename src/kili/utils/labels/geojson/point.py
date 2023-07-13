from typing import Any, Dict, List, Literal, Optional, Union


def kili_point_to_geojson_point(
    point: Dict[str, float]
) -> Dict[Literal["type", "coordinates"], Union[Literal["Point"], List[float]]]:
    """Convert a Kili point to a geojson point.

    Args:
        point: a Kili point (vertex):
            ```python
            {"x": 1.0, "y": 2.0}
            ```

    Returns:
        A geojson point:
            ```python
            {"type": "Point", "coordinates": [1.0, 2.0]}
            ```
    """
    return {"type": "Point", "coordinates": [point["x"], point["y"]]}


def kili_point_annotation_to_geojson_point_feature(
    point_annotation: Dict[str, Any], job_name: Optional[str] = None
) -> Dict[str, Any]:
    """Convert a Kili point annotation to a geojson point feature.

    Args:
        point_annotation: a Kili point annotation:
            ```python
            {
                'children': {},
                'point': {'x': -79.0, 'y': -3.0},
                'categories': [{'name': 'A'}],
                'mid': 'mid_object',
                'type': 'marker'
            }
            ```
        job_name: the name of the job to which the annotation belongs.

    Returns:
        A geojson point feature:
            ```python
            {
                'type': 'Feature',
                'geometry': {'type': 'Point',
                'coordinates': [-79.0, -3.0]},
                'id': 'mid_object',
                'properties': {'categories': [{'name': 'A'}]}
            }
            ```
    """
    point = point_annotation
    assert point["type"] == "marker", f"Annotation type must be `marker`, got: {point['type']}"

    ret = {"type": "Feature", "geometry": kili_point_to_geojson_point(point["point"])}
    if "mid" in point:
        ret["id"] = point["mid"]
    ret["properties"] = {k: v for k, v in point.items() if k not in ["point", "mid"]}
    if job_name is not None:
        ret["properties"]["job"] = job_name
    return ret


def geojson_point_feature_to_kili_point_annotation(point: Dict[str, Any]):
    """Convert a geojson point feature to a Kili point annotation."""
    assert point.get("type") == "Feature", f"Feature type must be `Feature`, got: {point['type']}"
    assert (
        point["geometry"]["type"] == "Point"
    ), f"Geometry type must be `Point`, got: {point['geometry']['type']}"

    ret = {
        "children": point["properties"].get("children", {}),
        "categories": point["properties"]["categories"],
        "type": "marker",
    }
    ret["point"] = {
        "x": point["geometry"]["coordinates"][0],
        "y": point["geometry"]["coordinates"][1],
    }
    if "id" in point:
        ret["mid"] = point["id"]
    return ret
