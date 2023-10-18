"""Set of functions to convert geojson to Kili format and vice versa."""

from .bbox import (
    geojson_polygon_feature_to_kili_bbox_annotation,
    kili_bbox_annotation_to_geojson_polygon_feature,
    kili_bbox_to_geojson_polygon,
)
from .collection import (
    features_to_feature_collection,
    geojson_feature_collection_to_kili_json_response,
    kili_json_response_to_feature_collection,
)
from .line import (
    geojson_linestring_feature_to_kili_line_annotation,
    kili_line_annotation_to_geojson_linestring_feature,
    kili_line_to_geojson_linestring,
)
from .point import (
    geojson_point_feature_to_kili_point_annotation,
    kili_point_annotation_to_geojson_point_feature,
    kili_point_to_geojson_point,
)
from .polygon import (
    geojson_polygon_feature_to_kili_polygon_annotation,
    kili_polygon_annotation_to_geojson_polygon_feature,
    kili_polygon_to_geojson_polygon,
)
from .segmentation import (
    geojson_polygon_feature_to_kili_segmentation_annotation,
    kili_segmentation_annotation_to_geojson_polygon_feature,
    kili_segmentation_to_geojson_polygon,
)

__all__ = [
    "features_to_feature_collection",
    "geojson_polygon_feature_to_kili_bbox_annotation",
    "geojson_polygon_feature_to_kili_polygon_annotation",
    "geojson_polygon_feature_to_kili_segmentation_annotation",
    "geojson_point_feature_to_kili_point_annotation",
    "geojson_linestring_feature_to_kili_line_annotation",
    "kili_bbox_annotation_to_geojson_polygon_feature",
    "kili_bbox_to_geojson_polygon",
    "kili_line_annotation_to_geojson_linestring_feature",
    "kili_line_to_geojson_linestring",
    "kili_point_annotation_to_geojson_point_feature",
    "kili_point_to_geojson_point",
    "kili_polygon_annotation_to_geojson_polygon_feature",
    "kili_polygon_to_geojson_polygon",
    "kili_segmentation_annotation_to_geojson_polygon_feature",
    "kili_segmentation_to_geojson_polygon",
    "kili_json_response_to_feature_collection",
    "geojson_feature_collection_to_kili_json_response",
]
