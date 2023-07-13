from typing import Any, Dict, List, Optional


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
