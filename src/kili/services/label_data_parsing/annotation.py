# Feature is still under development and is not yet suitable for use by general users.
"""Module for the "annotations" key parsing of a job response."""

import functools
from collections import defaultdict
from typing import Dict, List, Optional, Sequence

from typeguard import typechecked
from typing_extensions import Literal

from .bounding_poly import BoundingPoly
from .category import Category, CategoryList
from .decorators import for_all_properties
from .exceptions import AttributeNotCompatibleWithJobError, InvalidMutationError


class _BaseAnnotation:
    """Class for parsing the "annotations" key of a job response.

    It is used as a base class for the common properties of all types of annotations.
    """

    def __init__(self, annotation_json: Dict, job_interface: Dict) -> None:
        """Class for Annotation parsing.

        Args:
            annotation_json: Dict of an annotation. It is the value of
                the "annotations" key of a job response.
            job_interface: Job interface of the job.
        """
        self._json_data = annotation_json
        self._job_interface = job_interface

        self._is_required_job = job_interface["required"]

        # cast lists to objects
        if "categories" in self._json_data:
            self._json_data["categories"] = CategoryList(
                job_interface=self._job_interface, categories_list=self._json_data["categories"]
            )

    def __str__(self) -> str:
        return str(self._json_data)

    def __repr__(self) -> str:
        return repr(self._json_data)

    def as_dict(self) -> Dict:
        """Returns the parsed annotation as a dict."""
        ret = {k: v for k, v in self._json_data.items() if k not in ("categories",)}
        if "categories" in self._json_data:
            ret["categories"] = (
                self._json_data["categories"]
                if isinstance(self._json_data["categories"], List)
                else self._json_data["categories"].as_list()
            )
        return ret

    @property
    def categories(self) -> CategoryList:
        """Returns the list of categories of the annotation."""
        return self._json_data["categories"]

    @property
    def category(self) -> Category:
        """Returns the category of the annotation if there is only one category.

        Else raises an error.
        """
        if self._job_interface["content"]["input"] not in ("radio", "singleDropdown"):
            raise AttributeNotCompatibleWithJobError("category")

        if "categories" not in self._json_data and not self._is_required_job:
            return None  # type: ignore

        if len(self._json_data["categories"]) != 1:
            raise ValueError(f"Expected 1 category, got {self._json_data['categories']}")

        return self._json_data["categories"][0]

    @typechecked
    def add_category(self, name: str, confidence: Optional[int] = None) -> None:
        """Adds a category to an annotation job with categories."""
        if "categories" not in self._json_data:
            category_list = CategoryList(job_interface=self._job_interface, categories_list=[])
            category_list.add_category(name=name, confidence=confidence)
            self._json_data["categories"] = category_list
        else:
            self._json_data["categories"].add_category(name=name, confidence=confidence)

    @property
    def mid(self) -> str:
        """Returns the mid of the annotation."""
        return self._json_data["mid"]

    @mid.setter
    @typechecked
    def mid(self, mid: str) -> None:
        """Sets the mid of the annotation."""
        if len(mid) == 0:
            raise ValueError("mid must be non-empty.")
        self._json_data["mid"] = mid

    @property
    def children(self):
        """Not implemented yet."""


class EntityAnnotation(_BaseAnnotation):
    """Class for parsing the "annotations" key of a job response for named entities recognition."""

    @staticmethod
    def _get_compatible_ml_task() -> Literal["NAMED_ENTITIES_RECOGNITION"]:
        return "NAMED_ENTITIES_RECOGNITION"

    @property
    def begin_offset(self) -> int:
        """Returns the begin offset of the annotation."""
        return self._json_data["beginOffset"]

    @begin_offset.setter
    @typechecked
    def begin_offset(self, begin_offset: int) -> None:
        """Sets the begin offset of the annotation."""
        if begin_offset < 0:
            raise ValueError(f"begin_offset must be positive, got {begin_offset}")
        self._json_data["beginOffset"] = begin_offset

    @property
    def end_offset(self) -> int:
        """Returns the end offset of the annotation."""
        return self._json_data["endOffset"]

    @end_offset.setter
    @typechecked
    def end_offset(self, end_offset: int) -> None:
        """Sets the end offset of the annotation."""
        if end_offset < 0:
            raise ValueError(f"end_offset must be positive, got {end_offset}")
        self._json_data["endOffset"] = end_offset

    @property
    def content(self) -> str:
        """Returns the content of the annotation."""
        return self._json_data["content"]

    @content.setter
    @typechecked
    def content(self, content: str) -> None:
        """Sets the content of the annotation."""
        self._json_data["content"] = content


class _BaseAnnotationWithTool(_BaseAnnotation):
    """Base class for annotations with a "type" key (tool used to create the annotation)."""

    @property
    def type(self) -> Literal["rectangle", "polygon", "semantic", "marker", "vector", "polyline"]:
        """Returns the tool of the annotation.

        One of "rectangle", "polygon", or "semantic" for 2D annotations.

        One of "marker", "vector", "polyline" for 1D annotations.
        """
        return self._json_data["type"]


class PointAnnotation(_BaseAnnotationWithTool):
    """Class for parsing the "annotations" key of a job response for 1D object detection jobs."""

    @staticmethod
    def _get_compatible_ml_task() -> Literal["OBJECT_DETECTION"]:
        return "OBJECT_DETECTION"

    @staticmethod
    def _get_compatible_type_of_tools() -> Sequence[Literal["marker"]]:
        return ("marker",)

    @property
    def point(self) -> Dict[Literal["x", "y"], float]:
        """Returns the point of a point detection job."""
        return self._json_data["point"]

    @point.setter
    @typechecked
    def point(self, point: Dict[Literal["x", "y"], float]) -> None:
        """Sets the point of a point detection job."""
        self._json_data["point"] = point


class PolyLineAnnotation(_BaseAnnotationWithTool):
    """Class for parsing the "annotations" key of a job response for 1D object detection jobs."""

    @staticmethod
    def _get_compatible_ml_task() -> Literal["OBJECT_DETECTION"]:
        return "OBJECT_DETECTION"

    @staticmethod
    def _get_compatible_type_of_tools() -> Sequence[Literal["vector", "polyline"]]:
        return ("vector", "polyline")

    @property
    def polyline(self) -> List[Dict[Literal["x", "y"], float]]:
        """Returns the polyline of a polyline detection job."""
        return self._json_data["polyline"]

    @polyline.setter
    @typechecked
    def polyline(self, polyline: List[Dict[Literal["x", "y"], float]]) -> None:
        """Sets the polyline of a polyline detection job."""
        self._json_data["polyline"] = polyline


class _Base2DAnnotation(_BaseAnnotationWithTool):
    """Base class for 2D annotations."""

    @staticmethod
    def _get_compatible_ml_task() -> Literal["OBJECT_DETECTION"]:
        return "OBJECT_DETECTION"

    @staticmethod
    def _get_compatible_type_of_tools() -> (
        Sequence[Literal["rectangle", "polygon", "semantic", "polyline", "vector"]]
    ):
        return ("rectangle", "polygon", "semantic", "polyline", "vector")

    @property
    def bounding_poly(self) -> List[BoundingPoly]:
        """Returns the polygon of the object contour."""
        self._json_data["boundingPoly"] = [
            (BoundingPoly(p) if isinstance(p, dict) else p) for p in self._json_data["boundingPoly"]
        ]
        return self._json_data["boundingPoly"]

    @property
    def score(self) -> int:
        """Returns the score which is the confidence of the object detection.

        Available when a pre-annotation model is used.
        """
        return self._json_data["score"]

    @score.setter
    @typechecked
    def score(self, score: int) -> None:
        """Sets the score of the annotation."""
        if not 0 <= score <= 100:
            raise ValueError(f"Score must be between 0 and 100, got {score}")
        self._json_data["score"] = score


class BoundingPolyAnnotation(_Base2DAnnotation):
    """Class for parsing the "annotations" key of a job response for 2D object detection jobs."""


class VideoAnnotation(_Base2DAnnotation):
    """Class for parsing the "annotations" key of a job response for video object detection jobs."""

    @property
    def is_key_frame(self) -> bool:
        """Returns a boolean indicating if the timestamp or frame is used for interpolation."""
        try:
            return self._json_data["isKeyFrame"]
        except KeyError as err:
            raise AttributeNotCompatibleWithJobError("is_key_frame") from err


class PoseEstimationAnnotation(_BaseAnnotationWithTool):
    """Class for parsing the "annotations" key of a job response for pose estimation jobs."""

    @staticmethod
    def _get_compatible_ml_task() -> Literal["OBJECT_DETECTION"]:
        return "OBJECT_DETECTION"

    @staticmethod
    def _get_compatible_type_of_tools() -> Sequence[Literal["pose"]]:
        return ("pose",)

    @property
    def kind(self) -> Literal["POSE_ESTIMATION"]:
        """Returns the job kind.

        In pose estimation jobs, this is always "POSE_ESTIMATION".
        """
        return self._json_data["kind"]

    @property
    def points(self) -> List[Dict]:
        """Returns the list of the points composing the object."""
        return self._json_data["points"]


class EntityRelationAnnotation(_BaseAnnotation):
    """Class for parsing the "annotations" key of a job response for named entity relation jobs."""

    @staticmethod
    def _get_compatible_ml_task() -> Literal["NAMED_ENTITIES_RELATION"]:
        return "NAMED_ENTITIES_RELATION"

    @property
    def start_entities(self) -> List[Dict[Literal["mid"], str]]:
        """Returns the list of the start entities composing the relation."""
        return self._json_data["startEntities"]

    @start_entities.setter
    @typechecked
    def start_entities(self, start_entities: List[Dict[Literal["mid"], str]]) -> None:
        """Sets the list of the start entities composing the relation."""
        self._json_data["startEntities"] = start_entities

    @property
    def end_entities(self) -> List[Dict[Literal["mid"], str]]:
        """Returns the list of the end entities composing the relation."""
        return self._json_data["endEntities"]

    @end_entities.setter
    @typechecked
    def end_entities(self, end_entities: List[Dict[Literal["mid"], str]]) -> None:
        """Sets the list of the end entities composing the relation."""
        self._json_data["endEntities"] = end_entities


class ObjectRelationAnnotation(_BaseAnnotation):
    """Class for parsing the "annotations" key of a job response for object relation jobs."""

    @staticmethod
    def _get_compatible_ml_task() -> Literal["OBJECT_RELATION"]:
        return "OBJECT_RELATION"

    @property
    def start_objects(self) -> List[Dict[Literal["mid"], str]]:
        """Returns the list of the start objects composing the relation."""
        return self._json_data["startObjects"]

    @start_objects.setter
    @typechecked
    def start_objects(self, start_objects: List[Dict[Literal["mid"], str]]) -> None:
        """Sets the list of the start objects composing the relation."""
        self._json_data["startObjects"] = start_objects

    @property
    def end_objects(self) -> List[Dict[Literal["mid"], str]]:
        """Returns the list of the end objects composing the relation."""
        return self._json_data["endObjects"]

    @end_objects.setter
    @typechecked
    def end_objects(self, end_objects: List[Dict[Literal["mid"], str]]) -> None:
        """Sets the list of the end objects composing the relation."""
        self._json_data["endObjects"] = end_objects


def check_attribute_compatible_with_job(func):
    """Raises an error if the decorated method is not compatible with the job."""

    @functools.wraps(func)
    # pylint: disable=protected-access
    def wrapper(self, *args, **kwargs):
        attribute_name = func.__name__

        if attribute_name not in self._valid_attributes_for_ml_task[self._job_interface["mlTask"]]:
            raise AttributeNotCompatibleWithJobError(attribute_name)

        if (
            "type" in self._json_data
            and attribute_name not in self._valid_attributes_for_tool[self._json_data["type"]]
        ):
            raise AttributeNotCompatibleWithJobError(attribute_name)

        return func(self, *args, **kwargs)

    return wrapper


@for_all_properties(check_attribute_compatible_with_job)
# pylint: disable=too-many-ancestors
class Annotation(
    EntityAnnotation,
    PointAnnotation,
    PolyLineAnnotation,
    BoundingPolyAnnotation,
    VideoAnnotation,
    PoseEstimationAnnotation,
    EntityRelationAnnotation,
    ObjectRelationAnnotation,
):
    """Class for parsing the "annotations" key of a job response.

    Contains all attributes that can be found in a job response.
    """

    def __init__(self, json_data: Dict, job_interface: Dict) -> None:
        """Initializes an Annotation object.

        This class is used to parse the "annotations" key of a job response.

        Args:
            json_data: The json data of the annotation.
            job_interface: The job interface of the job.
        """
        super().__init__(annotation_json=json_data, job_interface=job_interface)

        # dictionaries to store the valid attributes/properties for each mlTask and type of tool
        self._valid_attributes_for_ml_task = defaultdict(set)
        self._valid_attributes_for_tool = defaultdict(set)

        for parent_class in self.__class__.__bases__:
            parent_class_methods = dir(parent_class)
            parent_class_properties = [
                method
                for method in parent_class_methods
                if isinstance(getattr(parent_class, method), property)
            ]

            ml_task = parent_class._get_compatible_ml_task()  # type: ignore
            self._valid_attributes_for_ml_task[ml_task].update(parent_class_properties)

            try:
                type_of_tools = parent_class._get_compatible_type_of_tools()  # type: ignore
            except AttributeError:
                continue

            for tool in type_of_tools:
                self._valid_attributes_for_tool[tool].update(parent_class_properties)

    # all properties should be inherited from the base classes


class AnnotationList:
    """Class for the annotations list parsing."""

    def __init__(self, annotations_list: List[Dict], job_interface: Dict) -> None:
        """Class for the annotations list parsing.

        Args:
            annotations_list: List of dicts representing annotations.
            job_interface: Job interface of the job.
        """
        self._annotations_list: List[Annotation] = []
        self._job_interface = job_interface

        for annotation_dict in annotations_list:
            self.add_annotation(annotation_dict)

    def _check_can_append_annotation(self, annotation: Annotation) -> None:
        # pylint: disable=protected-access
        if (
            "type" in annotation._json_data
            and annotation._json_data["type"] not in self._job_interface["tools"]
        ):
            raise InvalidMutationError(
                f"Annotation of type '{annotation._json_data['type']}' cannot be added to this job"
                f" with tools {self._job_interface['tools']}"
            )

    @typechecked
    def add_annotation(self, annotation_dict: Dict) -> None:
        """Adds an annotation object to the AnnotationList object."""
        annotation = Annotation(json_data=annotation_dict, job_interface=self._job_interface)
        self._check_can_append_annotation(annotation)
        self._annotations_list.append(annotation)

    @typechecked
    def __getitem__(self, index: int) -> Annotation:
        """Returns the annotation object at the given index."""
        return self._annotations_list[index]

    def __len__(self) -> int:
        """Returns the number of annotations."""
        return len(self._annotations_list)

    def __str__(self) -> str:
        """Returns the string representation of the annotations list."""
        return str(self.as_list())

    def __repr__(self) -> str:
        """Returns the string representation of the annotations list."""
        return repr(self.as_list())

    def as_list(self) -> List[Dict]:
        """Returns the list of categories as a list of dicts."""
        return [annotation.as_dict() for annotation in self._annotations_list]
