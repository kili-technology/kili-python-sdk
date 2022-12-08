"""
Types used by the conversion service
"""
from typing import NamedTuple, Tuple

from typing_extensions import Literal

ExportType = Literal["latest", "normal"]
SplitOption = Literal["split", "merged"]
LabelFormat = Literal["raw", "kili", "yolo_v4", "yolo_v5", "yolo_v7", "coco", "pascal_voc"]


class JobCategory(NamedTuple):
    """
    Contains information for a category
    """

    category_name: str
    id: int
    job_id: str


YoloAnnotation = Tuple[int, float, float, float, float]
