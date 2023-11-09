"""Ontology domain."""

from enum import Enum
from typing import NewType

JobName = NewType("JobName", str)


class JobMLTask(str, Enum):
    """List of ML Tasks."""

    ASSET_ANNOTATION = "ASSET_ANNOTATION"
    CLASSIFICATION = "CLASSIFICATION"
    NAMED_ENTITIES_RECOGNITION = "NAMED_ENTITIES_RECOGNITION"
    NAMED_ENTITIES_RELATION = "NAMED_ENTITIES_RELATION"
    OBJECT_RELATION = "OBJECT_RELATION"
    OBJECT_DETECTION = "OBJECT_DETECTION"
    PAGE_LEVEL_CLASSIFICATION = "PAGE_LEVEL_CLASSIFICATION"
    PAGE_LEVEL_TRANSCRIPTION = "PAGE_LEVEL_TRANSCRIPTION"
    POSE_ESTIMATION = "POSE_ESTIMATION"
    RANKING = "RANKING"
    SPEECH_TO_TEXT = "SPEECH_TO_TEXT"
    TRANSCRIPTION = "TRANSCRIPTION"


class JobTool(str, Enum):
    """List of tools."""

    MARKER = "marker"
    POLYGON = "polygon"
    POLYLINE = "polyline"
    POSE = "pose"
    RANGE = "range"
    RECTANGLE = "rectangle"
    SEMANTIC = "semantic"
    VECTOR = "vector"
