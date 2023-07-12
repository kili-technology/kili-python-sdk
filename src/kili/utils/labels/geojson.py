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


def kili_point_annotation_to_geojson_feature_point(
    point_annotation: Dict[str, Any]
) -> Dict[str, Any]:
    """Convert a Kili point annotation to a geojson feature point.

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
    point = point_annotation
    assert point["type"] == "marker", f"Annotation type must be `marker`, got: {point['type']}"
    ret = {"type": "Feature", "geometry": kili_point_to_geojson_point(point["point"])}
    if "mid" in point:
        ret["id"] = point["mid"]
    if "categories" in point:
        ret["properties"] = {}
        ret["properties"]["categories"] = point["categories"]
    return ret


def kili_bbox_to_geojson_polygon(normalized_vertices: List[Dict[str, float]]):
    """Convert a Kili bounding box to a geojson polygon.

    Args:
        normalized_vertices: a Kili bounding polygon normalized vertices.

    Returns:
        A geojson polygon:
            ```python
            {
                'type': 'Polygon',
                'coordinates': [
                    [
                        [4.426411498889343, 52.195226518404574],
                        [4.433707313141323, 52.195226518404574],
                        [4.433707313141323, 52.19969942041263],
                        [4.426411498889343, 52.19969942041263],
                        [4.426411498889343, 52.195226518404574]
                    ]
                ]
            }
            ```
    """
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


def kili_bbox_annotation_to_geojson_feature_polygon(bbox_annotation: Dict[str, Any]):
    """Convert a Kili bounding box annotation to a geojson feature polygon.

    Args:
        bbox_annotation: a Kili bounding box annotation:
            ```python
            {
                'children': {},
                'boundingPoly': [
                    {
                        'normalizedVertices': [...]
                    }
                ],
                'categories': [{'name': 'A'}],
                'mid': 'mid_object',
                'type': 'rectangle'
            }
            ```

    Returns:
        A geojson feature polygon:
            ```python
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [
                        [
                            ...
                        ]
                    ]
                },
                'id': 'mid_object',
                'properties': {'categories': [{'name': 'A'}]}
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
    if "categories" in bbox:
        ret["properties"] = {}
        ret["properties"]["categories"] = bbox["categories"]
    return ret


def kili_polygon_to_geojson_polygon(normalized_vertices: List[Dict[str, float]]):
    """Convert a Kili polygon to a geojson polygon."""
    ret = {"type": "Polygon", "coordinates": []}
    bbox = [[vertex["x"], vertex["y"]] for vertex in normalized_vertices]
    bbox.append(bbox[0])  # the first and last positions must be the same
    ret["coordinates"] = [bbox]
    return ret


def kili_polygon_annotation_to_geojson_feature_polygon(polygon_annotation: Dict[str, Any]):
    """Convert a Kili polygon annotation to a geojson feature polygon."""
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
    if "categories" in polygon:
        ret["properties"] = {}
        ret["properties"]["categories"] = polygon["categories"]
    return ret


def kili_line_to_geojson_linestring(
    polyline: List[Dict[str, float]]
) -> Dict[Literal["type", "coordinates"], Union[Literal["LineString"], List[List[float]]]]:
    """Convert a Kili line to a geojson linestring."""
    ret = {"type": "LineString", "coordinates": []}
    ret["coordinates"] = [[vertex["x"], vertex["y"]] for vertex in polyline]
    return ret  # type: ignore


def kili_line_annotation_to_geojson_feature_linestring(polyline_annotation: Dict[str, Any]):
    """Convert a Kili line annotation to a geojson feature linestring."""
    assert (
        polyline_annotation["type"] == "polyline"
    ), f"Annotation type must be `polyline`, got: {polyline_annotation['type']}"
    ret = {
        "type": "Feature",
        "geometry": kili_line_to_geojson_linestring(polyline_annotation["polyline"]),
    }
    if "mid" in polyline_annotation:
        ret["id"] = polyline_annotation["mid"]
    if "categories" in polyline_annotation:
        ret["properties"] = {}
        ret["properties"]["categories"] = polyline_annotation["categories"]
    return ret


def kili_segmentation_to_geojson_polygon(bounding_poly: List[Dict[str, List[Dict[str, Any]]]]):
    ret = {"type": "Polygon", "coordinates": []}
    for norm_vertices_dict in bounding_poly:
        bbox = [[vertex["x"], vertex["y"]] for vertex in norm_vertices_dict["normalizedVertices"]]
        bbox.append(bbox[0])  # the first and last positions must be the same
        ret["coordinates"].append(bbox)
    return ret


def kili_segmentation_annotation_to_geojson_feature_polygon(
    segmentation_annotation: Dict[str, Any]
):
    """Convert a Kili segmentation annotation to a geojson feature polygon."""
    assert (
        segmentation_annotation["type"] == "semantic"
    ), f"Annotation type must be `semantic`, got: {segmentation_annotation['type']}"
    ret = {
        "type": "Feature",
        "geometry": kili_segmentation_to_geojson_polygon(segmentation_annotation["boundingPoly"]),
    }
    if "mid" in segmentation_annotation:
        ret["id"] = segmentation_annotation["mid"]
    if "categories" in segmentation_annotation:
        ret["properties"] = {}
        ret["properties"]["categories"] = segmentation_annotation["categories"]
    return ret


def features_list_to_feature_collection(
    features: List[Dict],
) -> Dict[Literal["type", "features"], Union[str, List[Dict]]]:
    """Convert a list of features to a feature collection."""
    return {"type": "FeatureCollection", "features": features}
