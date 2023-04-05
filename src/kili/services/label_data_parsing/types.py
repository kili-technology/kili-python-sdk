"""Types for label data parsing module."""

from typing_extensions import TypedDict

from kili.core.enums import InputType
from kili.services.types import Jobs


class Project(TypedDict):
    """Project type."""

    inputType: InputType
    jsonInterface: Jobs
