"""
Types used by the conversion service
"""
from typing import NamedTuple, Tuple

from typing_extensions import Literal

ExportType = Literal["latest", "normal"]
SplitOption = Literal["split", "merged"]


class JobCategory(NamedTuple):
    """
    Contains information for a category
    """

    category_name: str
    id: int
    job_id: str


YoloAnnotation = Tuple[int, float, float, float, float]
