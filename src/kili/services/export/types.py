"""Types used by the conversion service."""

from typing import Callable, Dict, Literal, NamedTuple

ExportType = Literal["latest", "normal"]
SplitOption = Literal["split", "merged"]
LabelFormat = Literal[
    "raw", "kili", "yolo_v4", "yolo_v5", "yolo_v7", "yolo_v8", "coco", "pascal_voc", "geojson"
]


class JobCategory(NamedTuple):
    """Contains information for a category."""

    category_name: str
    id: int
    job_id: str


CocoAnnotationModifier = Callable[[Dict, Dict, Dict], Dict]
