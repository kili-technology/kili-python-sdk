"""Types for label data parsing module."""

from typing import Dict

from typing_extensions import Literal, TypedDict

from kili.core.enums import InputType
from kili.services.types import Jobs


class Project(TypedDict):
    """Project type."""

    inputType: InputType
    jsonInterface: Jobs


NormalizedVertex = Dict[Literal["x", "y"], float]
