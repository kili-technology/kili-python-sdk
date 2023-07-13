from typing import Any, Dict, List, Literal, Optional, Union


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
