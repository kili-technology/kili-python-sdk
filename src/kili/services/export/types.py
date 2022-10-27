"""
Types used by the conversion service
"""
from typing import Any, Dict, List, NamedTuple, Tuple

from typing_extensions import Literal, TypedDict

ExportType = Literal["latest", "normal"]
SplitOption = Literal["split", "merged"]
LabelFormat = Literal["raw", "yolo_v4", "yolo_v5", "yolo_v7", "coco"]


class JobCategory(NamedTuple):
    """
    Contains information for a category
    """

    category_name: str
    id: int
    job_id: str


YoloAnnotation = Tuple[int, float, float, float, float]


InputTypeT = Literal["IMAGE", "TEXT"]
MLTaskT = Literal["CLASSIFICATION", "NAMED_ENTITIES_RECOGNITION", "OBJECT_DETECTION"]
ToolT = Literal["rectangle", "semantic", "polygon"]
JobNameT = str
ProjectIdT = str


class JobT(TypedDict):
    content: Any
    instruction: str
    isChild: bool
    tools: List[ToolT]
    mlTask: MLTaskT
    models: Any  # example: {"interactive-segmentation": {"job": "SEMANTIC_JOB_MARKER"}},
    isVisible: bool
    required: int
    isNew: bool


JobsT = Dict[JobNameT, JobT]
