from typing import Any, Dict, List, Optional


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
