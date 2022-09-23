"""
Types used by the conversion service
"""
from typing import NamedTuple, NewType, Tuple, Union

from typing_extensions import Literal

InputType = Literal["TEXT", "IMAGE"]
AssetId = NewType("AssetId", str)
ProjectId = NewType("ProjectId", str)

LogLevel = Union[int, Literal["ERROR", "WARNING", "DEBUG", "INFO", "CRITICAL"]]


class JobCategory(NamedTuple):
    """
    Contains information for a category
    """

    category_name: str
    id: int
    job_id: str


YoloAnnotation = Tuple[int, float, float, float, float]
LabelType = Literal["AUTOSAVE", "DEFAULT", "PREDICTION", "REVIEW"]
