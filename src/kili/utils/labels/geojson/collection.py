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
    features = []

    annotation_tool_to_converter = {
        "rectangle": kili_bbox_annotation_to_geojson_polygon_feature,
        "marker": kili_point_annotation_to_geojson_point_feature,
        "polygon": kili_polygon_annotation_to_geojson_polygon_feature,
        "polyline": kili_line_annotation_to_geojson_linestring_feature,
        "semantic": kili_segmentation_annotation_to_geojson_polygon_feature,
    }

    for job_name, job_response in json_response.items():
        if "annotations" in job_response:
            for ann in job_response["annotations"]:
                annotation_tool = ann.get("type")
                if annotation_tool not in annotation_tool_to_converter:
                    continue

                converter = annotation_tool_to_converter[annotation_tool]
                feature = converter(ann, job_name=job_name)
                features.append(feature)

    return features_to_feature_collection(features)
