"""Types used by the conversion service."""

from collections.abc import Callable
from typing import Literal

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
