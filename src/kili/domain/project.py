"""Project domain."""
from typing import Literal, NewType

ProjectId = NewType("ProjectId", str)
InputType = Literal[
    "AUDIO",
    "IMAGE",
    "PDF",
    "TEXT",
    "TIME_SERIES",
    "VIDEO",
    "VIDEO_LEGACY",
]
