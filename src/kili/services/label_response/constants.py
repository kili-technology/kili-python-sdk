"""
Constants for the label_response service
"""
from enum import Enum


class MLTasks(Enum):
    """
    Machine learning tasks
    """

    CLASSIFICATION = "CLASSIFICATION"
    NAMED_ENTITIES_RECOGNITION = "NAMED_ENTITIES_RECOGNITION"
    NAMED_ENTITIES_RELATION = "NAMED_ENTITIES_RELATION"
    OBJECT_DETECTION = "OBJECT_DETECTION"
    OBJECT_RELATION = "OBJECT_RELATION"
    TRANSCRIPTION = "TRANSCRIPTION"


class Tools(Enum):
    """
    Possible tools for object detection tasks
    """

    MARKER = "marker"
    POLYGON = "polygon"
    POLYLINE = "polyline"
    POSE = "pose"
    RECTANGLE = "rectangle"
    SEMANTIC = "semantic"
    VECTOR = "vector"
