"""Types used by the conversion service."""

from typing import Dict, Literal, NewType, Union

from kili_formats.types import Job

InputType = Literal["TEXT", "IMAGE"]

LogLevel = Union[int, Literal["ERROR", "WARNING", "DEBUG", "INFO", "CRITICAL"]]


MLTask = Literal["CLASSIFICATION", "NAMED_ENTITIES_RECOGNITION", "OBJECT_DETECTION"]
Tool = Literal["rectangle", "semantic", "polygon"]
JobName = NewType("JobName", str)


Jobs = Dict[JobName, Job]
