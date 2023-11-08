"""Annotation domain."""

from typing import List, Literal, NewType, Optional, TypedDict, Union

from .label import LabelId
from .ontology import JobName

AnnotationId = NewType("AnnotationId", str)
KeyAnnotationId = NewType("KeyAnnotationId", str)


class Vertice(TypedDict):
    """Vertice."""

    x: float
    y: float


class ObjectDetectionAnnotationValue(TypedDict):
    """Object detection annotation value."""

    vertices: List[List[List[Vertice]]]


class ClassificationAnnotationValue(TypedDict):
    """Classification annotation value."""

    categories: List[str]


class TranscriptionAnnotationValue(TypedDict):
    """Transcription annotation value."""

    text: str


class Annotation(TypedDict):
    """Annotation."""

    id: AnnotationId
    labelId: LabelId
    job: JobName
    path: List[List[str]]


class FrameInterval(TypedDict):
    """Frame interval."""

    start: int
    end: int


class VideoObjectDetectionKeyAnnotation(TypedDict):
    """Video object detection key annotation."""

    id: KeyAnnotationId
    frame: int
    annotationValue: ObjectDetectionAnnotationValue


class VideoClassificationKeyAnnotation(TypedDict):
    """Video classification key annotation."""

    id: KeyAnnotationId
    frame: int
    annotationValue: ClassificationAnnotationValue


class VideoTranscriptionKeyAnnotation(TypedDict):
    """Video transcription key annotation."""

    id: KeyAnnotationId
    frame: int
    annotationValue: TranscriptionAnnotationValue


class VideoObjectDetectionAnnotation(TypedDict):
    """Video object detection annotation."""

    # pylint: disable=unused-private-member
    __typename: Literal["VideoObjectDetectionAnnotation"]
    id: AnnotationId
    labelId: LabelId
    job: JobName
    path: List[List[str]]
    frames: List[FrameInterval]
    keyAnnotations: List[VideoObjectDetectionKeyAnnotation]
    name: Optional[str]
    mid: str
    category: str


class VideoClassificationAnnotation(TypedDict):
    """Video classification annotation."""

    # pylint: disable=unused-private-member
    __typename: Literal["VideoClassificationAnnotation"]
    id: AnnotationId
    labelId: LabelId
    job: JobName
    path: List[List[str]]
    frames: List[FrameInterval]
    keyAnnotations: List[VideoClassificationKeyAnnotation]


class VideoTranscriptionAnnotation(TypedDict):
    """Video transcription annotation."""

    # pylint: disable=unused-private-member
    __typename: Literal["VideoTranscriptionAnnotation"]
    id: AnnotationId
    labelId: LabelId
    job: JobName
    path: List[List[str]]
    frames: List[FrameInterval]
    keyAnnotations: List[VideoTranscriptionKeyAnnotation]


VideoAnnotation = Union[
    VideoObjectDetectionAnnotation,
    VideoClassificationAnnotation,
    VideoTranscriptionAnnotation,
]
