import warnings
from typing import Any, Dict, List, Literal, Sequence, Union

from .bbox import kili_bbox_annotation_to_geojson_polygon_feature
from .line import kili_line_annotation_to_geojson_linestring_feature
from .point import kili_point_annotation_to_geojson_point_feature
from .polygon import kili_polygon_annotation_to_geojson_polygon_feature
from .segmentation import kili_segmentation_annotation_to_geojson_polygon_feature


def features_to_feature_collection(
    features: Sequence[Dict],
) -> Dict[Literal["type", "features"], Union[str, List[Dict]]]:
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


def kili_label_to_feature_collection(
    json_response: Dict[str, Any]
) -> Dict[Literal["type", "features"], Union[str, List[Dict]]]:
    """Convert a Kili label to a Geojson feature collection.

    Args:
        json_response: a Kili label.

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
        >>> kili_label_to_feature_collection(json_response)
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
            feature = converter(ann, job_name=job_name)
            features.append(feature)

    if jobs_skipped:
        warnings.warn(
            f"Jobs {jobs_skipped} do not have annotations and will be skipped.", stacklevel=2
        )
    if ann_tools_not_supported:
        warnings.warn(
            f"Annotation tools {ann_tools_not_supported} are not supported and will be skipped.",
            stacklevel=2,
        )
    return features_to_feature_collection(features)
