"""Utility functions to enrich GeoJSON features with Kili properties."""

from typing import Dict


# pylint: disable=too-many-statements,too-many-branches
def enrich_geojson_with_kili_properties(feature_collection: Dict, json_interface: Dict) -> Dict:
    """Enrich GeoJSON features with kili properties when missing.

    Args:
        feature_collection: The GeoJSON feature collection to enrich
        json_interface: The project's JSON interface containing job definitions

    Returns:
        The enriched feature collection with kili properties added where needed
    """
    object_detection_jobs = {}
    if "jobs" in json_interface:
        for job_name, job_config in json_interface["jobs"].items():
            if job_config.get("mlTask") == "OBJECT_DETECTION":
                object_detection_jobs[job_name] = job_config

    marker_job = None
    polyline_job = None
    polygon_job = None
    semantic_job = None

    for job_name, job_config in object_detection_jobs.items():
        tools = job_config.get("tools", [])
        if "marker" in tools and marker_job is None:
            marker_job = (job_name, job_config)
        if "polyline" in tools and polyline_job is None:
            polyline_job = (job_name, job_config)
        if "polygon" in tools and polygon_job is None:
            polygon_job = (job_name, job_config)
        if "semantic" in tools and semantic_job is None:
            semantic_job = (job_name, job_config)

    def get_first_category_name(job_config):
        categories = job_config.get("content", {}).get("categories", {})
        if categories:
            first_category_key = next(iter(categories.keys()))
            return first_category_key
        return None

    def create_kili_property(job_name, job_config, annotation_type):
        category_name = get_first_category_name(job_config)
        if category_name:
            return {
                "kili": {
                    "children": {},
                    "categories": [{"name": category_name}],
                    "type": annotation_type,
                    "job": job_name,
                }
            }
        return None

    enriched_features = []

    for feature in feature_collection.get("features", []):
        # Skip if feature already has kili properties
        if feature.get("properties", {}).get("kili") is not None:
            enriched_features.append(feature)
            continue

        # Skip features with null geometry unless they have kili properties
        if feature.get("geometry") is None:
            continue

        geometry_type = feature.get("geometry", {}).get("type")
        kili_property = None

        if geometry_type == "Point" and marker_job:
            job_name, job_config = marker_job
            kili_property = create_kili_property(job_name, job_config, "marker")

        elif geometry_type == "LineString" and polyline_job:
            job_name, job_config = polyline_job
            kili_property = create_kili_property(job_name, job_config, "polyline")

        elif geometry_type == "Polygon":
            if polygon_job:
                job_name, job_config = polygon_job
                kili_property = create_kili_property(job_name, job_config, "polygon")
            elif semantic_job:
                job_name, job_config = semantic_job
                kili_property = create_kili_property(job_name, job_config, "semantic")

        elif geometry_type == "MultiPolygon" and semantic_job:
            job_name, job_config = semantic_job
            kili_property = create_kili_property(job_name, job_config, "semantic")

        if kili_property:
            if "properties" not in feature:
                feature["properties"] = {}
            feature["properties"].update(kili_property)
            enriched_features.append(feature)
        else:
            continue

    enriched_collection = feature_collection.copy()
    enriched_collection["features"] = enriched_features
    return enriched_collection


# pylint: disable=too-many-branches
def enrich_geojson_with_specific_mapping(
    feature_collection: Dict, json_interface: Dict, target_job_name: str, target_category_name: str
) -> Dict:
    """Enrich GeoJSON features with specific job and category mapping.

    Args:
        feature_collection: The GeoJSON feature collection to enrich
        json_interface: The project's JSON interface containing job definitions
        target_job_name: The specific job name to map geometries to
        target_category_name: The specific category name to assign to all geometries

    Returns:
        The enriched feature collection with kili properties added
    """
    target_job_config = None
    if "jobs" in json_interface:
        target_job_config = json_interface["jobs"].get(target_job_name)

    if not target_job_config:
        raise ValueError(f"Job '{target_job_name}' not found in project")

    if target_job_config.get("mlTask") != "OBJECT_DETECTION":
        raise ValueError(f"Job '{target_job_name}' is not an OBJECT_DETECTION job")

    categories = target_job_config.get("content", {}).get("categories", {})
    if target_category_name not in categories:
        raise ValueError(f"Category '{target_category_name}' not found in job '{target_job_name}'")

    tools = target_job_config.get("tools", [])

    def create_kili_property(annotation_type: str):
        return {
            "kili": {
                "children": {},
                "categories": [{"name": target_category_name}],
                "type": annotation_type,
                "job": target_job_name,
            }
        }

    enriched_features = []

    for feature in feature_collection.get("features", []):
        # Skip features with null geometry
        if feature.get("geometry") is None:
            continue

        geometry_type = feature.get("geometry", {}).get("type")
        kili_property = None

        # Map geometry types to annotation types based on available tools
        if geometry_type == "Point" and "marker" in tools:
            kili_property = create_kili_property("marker")
        elif geometry_type == "LineString" and "polyline" in tools:
            kili_property = create_kili_property("polyline")
        elif geometry_type == "Polygon":
            if "polygon" in tools:
                kili_property = create_kili_property("polygon")
            elif "semantic" in tools:
                kili_property = create_kili_property("semantic")
        elif geometry_type == "MultiPolygon" and "semantic" in tools:
            kili_property = create_kili_property("semantic")

        if kili_property:
            if "properties" not in feature:
                feature["properties"] = {}
            feature["properties"].update(kili_property)
            enriched_features.append(feature)

    enriched_collection = feature_collection.copy()
    enriched_collection["features"] = enriched_features
    return enriched_collection
