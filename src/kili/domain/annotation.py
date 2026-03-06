"""Annotation domain."""

from typing import Literal, NewType, Optional, TypedDict, Union

from .label import LabelId
from .ontology import JobName

AnnotationId = NewType("AnnotationId", str)
AnnotationValueId = NewType("AnnotationValueId", str)
KeyAnnotationId = NewType("KeyAnnotationId", str)


class Vertice(TypedDict):
    """Vertice."""

    x: float
    y: float


class ObjectDetectionAnnotationValue(TypedDict):
    """Object detection annotation value."""

    vertices: list[list[list[Vertice]]]


class ClassificationAnnotationValue(TypedDict):
    """Classification annotation value."""

    categories: list[str]


class ClassificationAnnotation(TypedDict):
    """Classification annotation."""

    # pylint: disable=unused-private-member
    __typename: Literal["ClassificationAnnotation"]
    id: AnnotationId
    labelId: LabelId
    job: JobName
    path: list[list[str]]
    annotationValue: ClassificationAnnotationValue


class RankingOrderValue(TypedDict):
    """Ranking order value."""

    rank: int
    elements: list[str]


class TranscriptionAnnotationValue(TypedDict):
    """Transcription annotation value."""

    text: str


class TranscriptionAnnotation(TypedDict):
    """Transcription annotation."""

    # pylint: disable=unused-private-member
    __typename: Literal["TranscriptionAnnotation"]
    id: AnnotationId
    labelId: LabelId
    job: JobName
    path: list[list[str]]
    annotationValue: TranscriptionAnnotationValue


class ObjectDetectionAnnotation(TypedDict):
    """Object detection annotation."""

    # pylint: disable=unused-private-member
    __typename: Literal["ObjectDetectionAnnotation"]
    id: AnnotationId
    labelId: LabelId
    job: JobName
    path: list[list[str]]
    annotationValue: ObjectDetectionAnnotationValue
    name: Optional[str]
    mid: str
    category: str


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
    path: list[list[str]]
    frames: list[FrameInterval]
    keyAnnotations: list[VideoObjectDetectionKeyAnnotation]
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
    path: list[list[str]]
    frames: list[FrameInterval]
    keyAnnotations: list[VideoClassificationKeyAnnotation]


class VideoTranscriptionAnnotation(TypedDict):
    """Video transcription annotation."""

    # pylint: disable=unused-private-member
    __typename: Literal["VideoTranscriptionAnnotation"]
    id: AnnotationId
    labelId: LabelId
    job: JobName
    path: list[list[str]]
    frames: list[FrameInterval]
    keyAnnotations: list[VideoTranscriptionKeyAnnotation]


VideoAnnotation = Union[
    VideoObjectDetectionAnnotation,
    VideoClassificationAnnotation,
    VideoTranscriptionAnnotation,
]

ClassicAnnotation = Union[
    ClassificationAnnotation,
    ObjectDetectionAnnotation,
    TranscriptionAnnotation,
]

Annotation = Union[
    ClassificationAnnotation,
    TranscriptionAnnotation,
    VideoAnnotation,
]
