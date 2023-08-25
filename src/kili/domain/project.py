"""Project domain."""
from dataclasses import dataclass
from typing import Literal

InputType = Literal[
    "AUDIO",
    "IMAGE",
    "PDF",
    "TEXT",
    "TIME_SERIES",
    "VIDEO",
    "VIDEO_LEGACY",
]


@dataclass
class Project:
    """Project Entity."""

    id_: str
