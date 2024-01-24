"""Geojson collection module."""

import warnings
from typing import Any, Dict, Sequence

from .bbox import (
    geojson_polygon_feature_to_kili_bbox_annotation,
    kili_bbox_annotation_to_geojson_polygon_feature,
)
from .exceptions import (
    ConversionError,
)
from .line import (
    geojson_linestring_feature_to_kili_line_annotation,
    kili_line_annotation_to_geojson_linestring_feature,
)
from .point import (
    geojson_point_feature_to_kili_point_annotation,
    kili_point_annotation_to_geojson_point_feature,
)
from .polygon import (
    geojson_polygon_feature_to_kili_polygon_annotation,
    kili_polygon_annotation_to_geojson_polygon_feature,
)
from .segmentation import (
    geojson_polygon_feature_to_kili_segmentation_annotation,
    kili_segmentation_annotation_to_geojson_polygon_feature,
)


def features_to_feature_collection(
    features: Sequence[Dict],
) -> Dict[str, Any]:
    """Convert a list of features to a feature collection.

    Args:
        features: a list of Geojson features.

    Returns:
        A Geojson feature collection.

    !!! Example
        ```python
        >>> features = [
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-79.0, -3.0]},
                    'id': '1',
                }
            },
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-79.0, -3.0]},
                    'id': '2',
                }
            }
        ]
        >>> features_to_feature_collection(features)
        {
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [-79.0, -3.0]},
                        'id': '1',
                    }
                },
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [-79.0, -3.0]},
                        'id': '2',
                    }
                }
            ]
        }
        ```
    """
    return {"type": "FeatureCollection", "features": list(features)}


def kili_json_response_to_feature_collection(json_response: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a Kili label json response to a Geojson feature collection.

    Args:
        json_response: a Kili label json response.

    Returns:
        A Geojson feature collection.

    !!! Example
        ```python
        >>> json_response = {
            'job_1': {
                'annotations': [...]
            },
            'job_2': {
                'annotations': [...]
            }
        }
        >>> kili_json_response_to_feature_collection(json_response)
        {
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'geometry': {
                        ...
                    }
                },
                {
                    'type': 'Feature',
                    'geometry': {
                        ...
                    }
                }
            ]
        }
        ```
    """
    features = []

    annotation_tool_to_converter = {
        "rectangle": kili_bbox_annotation_to_geojson_polygon_feature,
        "marker": kili_point_annotation_to_geojson_point_feature,
        "polygon": kili_polygon_annotation_to_geojson_polygon_feature,
        "polyline": kili_line_annotation_to_geojson_linestring_feature,
        "semantic": kili_segmentation_annotation_to_geojson_polygon_feature,
    }

    jobs_skipped = []
    ann_tools_not_supported = set()
    for job_name, job_response in json_response.items():
        if "annotations" not in job_response:
            jobs_skipped.append(job_name)
            continue

        for ann in job_response["annotations"]:
            annotation_tool = ann.get("type")
            if annotation_tool not in annotation_tool_to_converter:
                ann_tools_not_supported.add(annotation_tool)
                continue

            converter = annotation_tool_to_converter[annotation_tool]

            try:
                feature = converter(ann, job_name=job_name)
                features.append(feature)
            except ConversionError as error:
                warnings.warn(
                    error.args[0],
                    stacklevel=2,
                )
                continue

    if jobs_skipped:
        warnings.warn(f"Jobs {jobs_skipped} cannot be exported to GeoJson format.", stacklevel=2)
    if ann_tools_not_supported:
        warnings.warn(
            f"Annotation tools {ann_tools_not_supported} are not supported and will be skipped.",
            stacklevel=2,
        )
    return features_to_feature_collection(features)


def geojson_feature_collection_to_kili_json_response(
    feature_collection: Dict[str, Any],
) -> Dict[str, Any]:
    # pylint: disable=line-too-long
    """Convert a Geojson feature collection to a Kili label json response.

    Args:
        feature_collection: a Geojson feature collection.

    Returns:
        A Kili label json response.

    !!! Warning
        This method requires the `kili` key to be present in the geojson features' properties.
        In particular, the `kili` dictionary of a feature must contain the `categories` and `type` of the annotation.
        It must also contain the `job` name.

    !!! Example
        ```python
        >>> feature_collection = {
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'geometry': {
                        ...
                    },
                    'properties': {
                        'kili': {
                            'categories': [{'name': 'A'}],
                            'type': 'marker',
                            'job': 'POINT_DETECTION_JOB'
                        }
                    }
                },
            ]
        }
        >>> geojson_feature_collection_to_kili_json_response(feature_collection)
        {
            'POINT_DETECTION_JOB': {
                'annotations': [
                    {
                        'categories': [{'name': 'A'}],
                        'type': 'marker',
                        'point': ...
                    }
                ]
            }
        }
        ```
    """
    assert (
        feature_collection["type"] == "FeatureCollection"
    ), f"Feature collection type must be `FeatureCollection`, got: {feature_collection['type']}"

    annotation_tool_to_converter = {
        "rectangle": geojson_polygon_feature_to_kili_bbox_annotation,
        "marker": geojson_point_feature_to_kili_point_annotation,
        "polygon": geojson_polygon_feature_to_kili_polygon_annotation,
        "polyline": geojson_linestring_feature_to_kili_line_annotation,
        "semantic": geojson_polygon_feature_to_kili_segmentation_annotation,
    }

    json_response = {}

    for feature in feature_collection["features"]:
        if feature.get("properties").get("kili", {}).get("job") is None:
            raise ValueError(f"Job name is missing in the GeoJson feature {feature}")

        job_name = feature["properties"]["kili"]["job"]

        if feature.get("properties").get("kili", {}).get("type") is None:
            raise ValueError(f"Annotation `type` is missing in the GeoJson feature {feature}")

        annotation_tool = feature["properties"]["kili"]["type"]

        if annotation_tool not in annotation_tool_to_converter:
            raise ValueError(f"Annotation tool {annotation_tool} is not supported.")

        kili_annotation = annotation_tool_to_converter[annotation_tool](feature)

        if job_name not in json_response:
            json_response[job_name] = {}
        if "annotations" not in json_response[job_name]:
            json_response[job_name]["annotations"] = []

        json_response[job_name]["annotations"].append(kili_annotation)

    return json_response
