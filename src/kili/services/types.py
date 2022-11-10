"""
Types used by the conversion service
"""
from typing import Any, Dict, List, NamedTuple, NewType, Tuple, Union

from typing_extensions import Literal, TypedDict

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
LabelType = Literal["AUTOSAVE", "DEFAULT", "PREDICTION", "REVIEW", "INFERENCE"]

InputType = Literal["IMAGE", "TEXT"]
MLTask = Literal["CLASSIFICATION", "NAMED_ENTITIES_RECOGNITION", "OBJECT_DETECTION"]
Tool = Literal["rectangle", "semantic", "polygon"]
JobName = NewType("JobName", str)
ProjectId = NewType("ProjectId", str)


class Job(TypedDict):
    """
    Contains job settings
    """

    content: Any
    instruction: str
    isChild: bool
    tools: List[Tool]
    mlTask: MLTask
    models: Any  # example: {"interactive-segmentation": {"job": "SEMANTIC_JOB_MARKER"}},
    isVisible: bool
    required: int
    isNew: bool


Jobs = Dict[JobName, Job]
