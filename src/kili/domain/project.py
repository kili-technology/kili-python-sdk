"""Project domain."""
from typing import Literal, NewType

ProjectId = NewType("ProjectId", str)
InputType = Literal[
    "IMAGE",
    "PDF",
    "TEXT",
    "VIDEO",
    "VIDEO_LEGACY",
]
