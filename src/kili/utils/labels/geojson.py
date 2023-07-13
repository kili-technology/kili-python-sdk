"""Set of utils to handle geojson labels.

Kili format: geospatial labels `x` stands for longitude and `y` for latitude.

Geojson format: Points are [x, y] or [x, y, z]. They may be [longitude, latitude].
Elevation `z` is an optional third number. They are decimal numbers.
"""
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


def kili_bbox_annotation_to_geojson_polygon_feature(
    bbox_annotation: Dict[str, Any], job_name: Optional[str] = None
):
    """Convert a Kili bounding box annotation to a geojson polygon feature.

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
        job_name: the name of the job to which the annotation belongs.

    Returns:
        A geojson polygon feature:
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
    ret["properties"] = {k: v for k, v in bbox.items() if k not in ["boundingPoly", "mid"]}
    if job_name is not None:
        ret["properties"]["job"] = job_name
    return ret


def kili_polygon_to_geojson_polygon(normalized_vertices: List[Dict[str, float]]):
    """Convert a Kili polygon to a geojson polygon."""
    ret = {"type": "Polygon", "coordinates": []}
    bbox = [[vertex["x"], vertex["y"]] for vertex in normalized_vertices]
    bbox.append(bbox[0])  # the first and last positions must be the same
    ret["coordinates"] = [bbox]
    return ret


def kili_polygon_annotation_to_geojson_polygon_feature(
    polygon_annotation: Dict[str, Any], job_name: Optional[str] = None
):
    """Convert a Kili polygon annotation to a geojson polygon feature."""
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
    ret["properties"] = {k: v for k, v in polygon.items() if k not in ["boundingPoly", "mid"]}
    if job_name is not None:
        ret["properties"]["job"] = job_name
    return ret


def kili_line_to_geojson_linestring(
    polyline: List[Dict[str, float]]
) -> Dict[Literal["type", "coordinates"], Union[Literal["LineString"], List[List[float]]]]:
    """Convert a Kili line to a geojson linestring."""
    ret = {"type": "LineString", "coordinates": []}
    ret["coordinates"] = [[vertex["x"], vertex["y"]] for vertex in polyline]
    return ret  # type: ignore


def kili_line_annotation_to_geojson_linestring_feature(
    polyline_annotation: Dict[str, Any], job_name: Optional[str] = None
):
    """Convert a Kili line annotation to a geojson linestring feature."""
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
        k: v for k, v in polyline_annotation.items() if k not in ["mid", "polyline"]
    }
    if job_name is not None:
        ret["properties"]["job"] = job_name
    return ret


def kili_segmentation_to_geojson_polygon(bounding_poly: List[Dict[str, List[Dict[str, Any]]]]):
    ret = {"type": "Polygon", "coordinates": []}
    for norm_vertices_dict in bounding_poly:
        bbox = [[vertex["x"], vertex["y"]] for vertex in norm_vertices_dict["normalizedVertices"]]
        bbox.append(bbox[0])  # the first and last positions must be the same
        ret["coordinates"].append(bbox)
    return ret


def kili_segmentation_annotation_to_geojson_polygon_feature(
    segmentation_annotation: Dict[str, Any], job_name: Optional[str] = None
):
    """Convert a Kili segmentation annotation to a geojson polygon feature."""
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
        k: v for k, v in segmentation_annotation.items() if k not in ["mid", "boundingPoly"]
    }
    if job_name is not None:
        ret["properties"]["job"] = job_name
    return ret


def features_list_to_feature_collection(
    features: List[Dict],
) -> Dict[Literal["type", "features"], Union[str, List[Dict]]]:
    """Convert a list of features to a feature collection."""
    return {"type": "FeatureCollection", "features": features}


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


def geojson_polygon_feature_to_kili_bbox_annotation(polygon: Dict[str, Any]):
    """Convert a geojson polygon feature to a Kili bounding box annotation."""
    assert (
        polygon.get("type") == "Feature"
    ), f"Feature type must be `Feature`, got: {polygon['type']}"
    assert (
        polygon["geometry"]["type"] == "Polygon"
    ), f"Geometry type must be `Polygon`, got: {polygon['geometry']['type']}"

    ret = {
        "children": polygon["properties"].get("children", {}),
        "categories": polygon["properties"]["categories"],
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
    if "id" in polygon:
        ret["mid"] = polygon["id"]
    return ret


def geojson_polygon_feature_to_kili_polygon_annotation(polygon: Dict[str, Any]):
    """Convert a geojson polygon feature to a Kili polygon annotation."""
    assert (
        polygon.get("type") == "Feature"
    ), f"Feature type must be `Feature`, got: {polygon['type']}"
    assert (
        polygon["geometry"]["type"] == "Polygon"
    ), f"Geometry type must be `Polygon`, got: {polygon['geometry']['type']}"

    ret = {
        "children": polygon["properties"].get("children", {}),
        "categories": polygon["properties"]["categories"],
        "type": "polygon",
    }
    coords = polygon["geometry"]["coordinates"][0]
    normalized_vertices = [{"x": coord[0], "y": coord[1]} for coord in coords[:-1]]
    ret["boundingPoly"] = [{"normalizedVertices": normalized_vertices}]
    if "id" in polygon:
        ret["mid"] = polygon["id"]
    return ret


def geojson_linestring_feature_to_kili_line_annotation(line: Dict[str, Any]):
    """Convert a geojson linestring feature to a Kili line annotation."""
    assert line.get("type") == "Feature", f"Feature type must be `Feature`, got: {line['type']}"
    assert (
        line["geometry"]["type"] == "LineString"
    ), f"Geometry type must be `LineString`, got: {line['geometry']['type']}"

    ret = {
        "children": line["properties"].get("children", {}),
        "categories": line["properties"]["categories"],
        "type": "polyline",
    }
    ret["polyline"] = [{"x": coord[0], "y": coord[1]} for coord in line["geometry"]["coordinates"]]
    if "id" in line:
        ret["mid"] = line["id"]
    return ret


def geojson_polygon_feature_to_kili_segmentation_annotation(polygon: Dict[str, Any]):
    """Convert a geojson polygon feature to a Kili segmentation annotation."""
    assert (
        polygon.get("type") == "Feature"
    ), f"Feature type must be `Feature`, got: {polygon['type']}"
    assert (
        polygon["geometry"]["type"] == "Polygon"
    ), f"Geometry type must be `Polygon`, got: {polygon['geometry']['type']}"

    ret = {
        "children": polygon["properties"].get("children", {}),
        "categories": polygon["properties"]["categories"],
        "type": "semantic",
    }
    coords = polygon["geometry"]["coordinates"]
    ret["boundingPoly"] = [
        {"normalizedVertices": [{"x": coord[0], "y": coord[1]} for coord in polygon[:-1]]}
        for polygon in coords
    ]
    if "id" in polygon:
        ret["mid"] = polygon["id"]
    return ret
