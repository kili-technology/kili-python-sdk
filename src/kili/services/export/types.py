"""Types used by the conversion service."""

from typing import Callable, Dict, Literal

ExportType = Literal["latest", "normal"]
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


CocoAnnotationModifier = Callable[[Dict, Dict, Dict], Dict]
