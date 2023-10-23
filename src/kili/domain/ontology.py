"""Ontology domain."""

from dataclasses import dataclass


@dataclass
class JobMLTask:
    """List of ML Tasks."""

    AssetAnnotation = "ASSET_ANNOTATION"
    Classification = "CLASSIFICATION"
    NamedEntitiesRecognition = "NAMED_ENTITIES_RECOGNITION"
    NamedEntitiesRelation = "NAMED_ENTITIES_RELATION"
    ObjectRelation = "OBJECT_RELATION"
    ObjectDetection = "OBJECT_DETECTION"
    PoseEstimation = "POSE_ESTIMATION"
    RegionDetection = "REGION_DETECTION"
    SpeechToText = "SPEECH_TO_TEXT"
    Transcription = "TRANSCRIPTION"


@dataclass
class JobTool:
    """List of tools."""

    Marker = "marker"
    Polygon = "polygon"
    Polyline = "polyline"
    Range = "range"
    Rectangle = "rectangle"
    Semantic = "semantic"
    Vector = "vector"
