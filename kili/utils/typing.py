"""Common typings """
from enum import Enum


class InputType(Enum):
    """Input Types."""

    AUDIO = "AUDIO"
    FRAME = "FRAME"
    IMAGE = "IMAGE"
    PDF = "PDF"
    TEXT = "TEXT"
    TIME_SERIES = "TIME_SERIES"
    VIDEO = "VIDEO"
    VIDEO_LEGACY = "VIDEO_LEGACY"


class Status(Enum):
    """Asset Status."""

    TODO = "TODO"
    ONGOING = "ONGOING"
    LABELED = "LABELED"
    TO_REVIEW = "TO_REVIEW"
    REVIEWED = "REVIEWED"
