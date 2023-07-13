"""Geojson linestring utilities."""
from typing import Any, Dict, List, Literal, Optional, Union


def kili_line_to_geojson_linestring(
    polyline: List[Dict[str, float]]
) -> Dict[Literal["type", "coordinates"], Union[Literal["LineString"], List[List[float]]]]:
    """Convert a Kili line to a geojson linestring.

    Args:
        polyline: a Kili line (polyline).

    Returns:
        A geojson linestring.

    !!! Example
        ```python
        >>> polyline = [{"x": 1.0, "y": 2.0}, {"x": 3.0, "y": 4.0}]
        >>> kili_line_to_geojson_linestring(polyline)
        {
            "type": "LineString",
            "coordinates": [[1.0, 2.0], [3.0, 4.0]]
        }
        ```
    """
    ret = {"type": "LineString", "coordinates": []}
    ret["coordinates"] = [[vertex["x"], vertex["y"]] for vertex in polyline]
    return ret  # type: ignore


def kili_line_annotation_to_geojson_linestring_feature(
    polyline_annotation: Dict[str, Any], job_name: Optional[str] = None
) -> Dict[str, Any]:
    """Convert a Kili line annotation to a geojson linestring feature.

    Args:
        polyline_annotation: a Kili line annotation.
        job_name: the name of the job to which the annotation belongs.

    Returns:
        A geojson linestring feature.

    !!! Example
        ```python
        >>> polyline = {
            'children': {},
            'polyline': [{'x': -79.0, 'y': -3.0}, {'x': -79.0, 'y': -3.0}],
            'categories': [{'name': 'A'}],
            'mid': 'mid_object',
            'type': 'polyline'
        }
        >>> kili_line_annotation_to_geojson_linestring_feature(polyline, 'job_name')
        {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [[-79.0, -3.0], [-79.0, -3.0]]},
                'id': 'mid_object',
                'properties': {
                    'kili': {
                        'categories': [{'name': 'A'}],
                        'children': {},
                        'job': 'job_name'
                    }
                }
        }
        ```
    """
    assert (
        polyline_annotation["type"] == "polyline"
    ), f"Annotation type must be `polyline`, got: {polyline_annotation['type']}"

    ret = {
        "type": "Feature",
        "geometry": kili_line_to_geojson_linestring(polyline_annotation["polyline"]),
    }
    if "mid" in polyline_annotation:
        ret["id"] = polyline_annotation["mid"]
    ret["properties"] = {
        "kili": {k: v for k, v in polyline_annotation.items() if k not in ["mid", "polyline"]}
    }
    if job_name is not None:
        ret["properties"]["kili"]["job"] = job_name
    return ret


def geojson_linestring_feature_to_kili_line_annotation(line: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a geojson linestring feature to a Kili line annotation.

    Args:
        line: a geojson linestring feature.

    Returns:
        A Kili line annotation.

    !!! Example
        ```python
        >>> line = {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [[-79.0, -3.0], [-79.0, -3.0]]},
                'id': 'mid_object',
                'properties': {
                    'kili': {
                        'categories': [{'name': 'A'}],
                        'children': {},
                        'job': 'job_name'
                    }
                }
        }
        >>> geojson_linestring_feature_to_kili_line_annotation(line)
        {
            'children': {},
            'polyline': [{'x': -79.0, 'y': -3.0}, {'x': -79.0, 'y': -3.0}],
            'categories': [{'name': 'A'}],
            'mid': 'mid_object',
            'type': 'polyline'
        }
        ```
    """
    assert line["type"] == "Feature", f"Feature type must be `Feature`, got: {line['type']}"
    assert (
        line["geometry"]["type"] == "LineString"
    ), f"Geometry type must be `LineString`, got: {line['geometry']['type']}"

    ret = {
        "children": line["properties"].get("kili", {}).get("children", {}),
        "categories": line["properties"]["kili"]["categories"],
        "type": "polyline",
    }
    ret["polyline"] = [{"x": coord[0], "y": coord[1]} for coord in line["geometry"]["coordinates"]]
    if "id" in line:
        ret["mid"] = line["id"]
    return ret
