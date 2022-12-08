"""
This script defines object-relational mapping helpers to ease
 the manipulation of Kili data structures.
"""
from dataclasses import dataclass

from typing_extensions import Literal


class DictClass(dict):
    """
    A python class that acts like dict
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


AnnotationFormat = Literal[
    "kili", "raw", "simple", "yolo_v4", "yolo_v5", "yolo_v7", "coco", "pascal_voc"
]


@dataclass
class AssetStatus:
    # pylint: disable=invalid-name
    """
    List of asset status
    """
    Labeled = "LABELED"
    Ongoing = "ONGOING"
    Reviewed = "REVIEWED"
    ToReview = "TO_REVIEW"
    Todo = "TODO"


@dataclass
class JobMLTask:
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    """
    List of ML Tasks
    """
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
    # pylint: disable=invalid-name
    """
    List of tools
    """
    Marker = "marker"
    Polygon = "polygon"
    Polyline = "polyline"
    Range = "range"
    Rectangle = "rectangle"
    Semantic = "semantic"
    Vector = "vector"


def get_polygon(annotation):
    """
    Extracts a polygon from an annotation

    Args:
        annotation : Kili annotation
    """
    try:
        return annotation["boundingPoly"][0]["normalizedVertices"]
    except KeyError:
        return None


def get_category(annotation):
    """
    Extracts a category from an annotation

    Args:
        annotation : Kili annotation
    """
    try:
        return annotation["categories"][0]["name"]
    except KeyError:
        return None


def get_named_entity(annotation):
    """
    Extracts a named entity from an annotation

    Args:
        annotation : Kili annotation
    """
    try:
        return {
            "beginId": annotation["beginId"],
            "beginOffset": annotation["beginOffset"],
            "content": annotation["content"],
            "endId": annotation["endId"],
            "endOffset": annotation["endOffset"],
        }
    except KeyError:
        return None


def format_image_annotation(annotation):
    """
    Extracts a category, polygon, named entity from an annotation
    depending of the annotation type

    Args:
        annotation : Kili annotation
    """
    category = get_category(annotation)
    polygon = get_polygon(annotation)
    named_entity = get_named_entity(annotation)
    if polygon is not None:
        return (category, polygon)
    if named_entity is not None:
        return (category, named_entity)
    if category is not None:
        return category
    return None


class Label(DictClass):
    """
    Label class
    """

    jsonResponse = {}

    def json_response(self, _format: AnnotationFormat = "raw"):
        """
        Format a json response

        Args:
            _format: expected format
        """
        if "jsonResponse" not in self:
            raise Exception(
                f'You did not fetch jsonResponse for label "{self["id"] if "id" in self else self}"'
            )
        if _format == "simple":
            job_names = self.jsonResponse.keys()
            if len(job_names) > 1:
                return {
                    "error": (
                        "Simple format is not adapted"
                        " when there is more than one job."
                        " Please choose another annotation format."
                    )
                }
            for job_name in job_names:
                job_response = self.jsonResponse[job_name]
                category = get_category(job_response)
                if category is not None:
                    return category
                if "annotations" not in job_response:
                    return None
                return [
                    format_image_annotation(annotation)
                    for annotation in job_response["annotations"]
                ]
            return None
        return self.jsonResponse


class Asset(DictClass):
    """
    Asset class
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "labels" in self:
            labels = []
            for label in self["labels"]:
                labels.append(Label(label))
            self.labels = labels
        if "latestLabel" in self:
            latest_label = self["latestLabel"]
            if latest_label is not None:
                self.latestLabel = Label(latest_label)  # pylint: disable=invalid-name
