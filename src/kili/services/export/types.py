"""Types used by the conversion service."""

from collections.abc import Callable
from typing import Literal

# How a YOLO v5, v7 or v8 export writes the bounding boxes, as kili-formats lays it out
from kili_formats.layout import YoloBoundingBoxes  # noqa: F401  # pylint: disable=unused-import

ExportType = Literal["latest", "latest_from_last_step", "latest_from_all_steps", "normal"]
SplitOption = Literal["split", "merged"]
LabelFormat = Literal[
    "raw",
    "kili",
    "yolo_v4",
    "yolo_v5",
    "yolo_v7",
    "yolo_v8",
    "coco",
    "pascal_voc",
    "geojson",
]


CocoAnnotationModifier = Callable[[dict, dict, dict], dict]
