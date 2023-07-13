from typing import Any, Dict, List, Optional


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
