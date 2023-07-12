"""Set of utils to handle geojson labels.

Kili format: geospatial labels `x` stands for longitude and `y` for latitude.

Geojson format: Points are [x, y] or [x, y, z]. They may be [longitude, latitude].
Elevation is an optional third number. They are decimal numbers.
"""
from typing import Any, Dict, List, Literal, Union


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


def kili_point_annotation_to_geojson_feature_point(point: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a Kili point annotation to a geojson feature point.

    Args:
        point: a Kili point annotation:
            ```python
            {
                'children': {},
                'point': {'x': -79.0, 'y': -3.0},
                'categories': [{'name': 'A'}],
                'mid': 'mid_object',
                'type': 'marker'
            }
            ```

    Returns:
        A geojson feature point:
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
    ret = {"type": "Feature", "geometry": kili_point_to_geojson_point(point["point"])}
    if "mid" in point:
        ret["id"] = point["mid"]
    if "categories" in point:
        ret["properties"] = {}
        ret["properties"]["categories"] = point["categories"]
    return ret


def kili_bbox_to_geojson_polygon(normalized_vertices: List[Dict[str, float]]):
    """Convert a Kili bounding box to a geojson polygon."""
    vertex_name_to_value = {}
    for vertex, point_name in zip(
        normalized_vertices, ("bottom_left", "top_left", "top_right", "bottom_right")
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


def kili_bbox_annotation_to_geojson_polygon(bbox: Dict[str, Any]):
    """Convert a Kili bounding box annotation to a geojson feature polygon."""
    assert bbox["type"] == "rectangle", f"Annotation type must be `rectangle`, got: {bbox['type']}"
    ret = {
        "type": "Feature",
        "geometry": kili_bbox_to_geojson_polygon(bbox["boundingPoly"][0]["normalizedVertices"]),
    }
    if "mid" in bbox:
        ret["id"] = bbox["mid"]
    if "categories" in bbox:
        ret["properties"] = {}
        ret["properties"]["categories"] = bbox["categories"]
    return ret
