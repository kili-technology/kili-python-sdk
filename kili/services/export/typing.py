"""
Types used by the conversion service
"""
from typing import NamedTuple, NewType, Tuple, Union

from typing_extensions import Literal

LabelFormat = Literal["yolo_v4", "yolo_v5"]
InputType = Literal["TEXT", "IMAGE"]
ExportType = Literal["latest", "normal"]
AssetId = NewType("AssetId", str)
ProjectId = NewType("ProjectId", str)
SplitOption = Literal["split", "merged"]
LogLevel = Union[int, Literal["ERROR", "WARNING", "DEBUG", "INFO", "CRITICAL"]]


class JobCategory(NamedTuple):
    """
    Contains information for a category
    """

    category_name: str
    id: int
    job_id: str


YoloAnnotation = Tuple[int, float, float, float, float]
