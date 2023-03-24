# Feature is still under development and is not yet suitable for use by general users.
"""Module for the "annotations" key parsing of a job response."""

import functools
from collections import defaultdict
from typing import Dict, List, Sequence

from typing_extensions import Literal

from .bounding_poly import BoundingPoly
from .category import Category, CategoryList
from .decorators import for_all_properties
from .exceptions import AttributeNotCompatibleWithJobError


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
        self.json_data: Dict = annotation_json
        self.job_interface: Dict = job_interface

        self.is_required_job = job_interface["required"]

        self._cast_categories()

    def _cast_categories(self) -> None:
        """Casts the categories list of the job payload to CategoryList object."""
        if "categories" not in self.json_data:
            return

        if not isinstance(self.json_data["categories"], CategoryList):
            self.json_data["categories"] = CategoryList(
                self.job_interface, self.json_data["categories"]
            )

    @property
    def categories(self) -> CategoryList:
        """Returns the list of categories of the annotation."""
        return self.json_data["categories"]

    @property
    def category(self) -> Category:
        """Returns the category of the annotation if there is only one category.

        Else raises an error.
        """
        if self.job_interface["content"]["input"] not in ("radio", "singleDropdown"):
            raise AttributeNotCompatibleWithJobError("category")

        if "categories" not in self.json_data and not self.is_required_job:
            return None  # type: ignore

        return self.json_data["categories"][0]

    @property
    def mid(self) -> str:
        """Returns the mid of the annotation."""
        return self.json_data["mid"]


class EntityAnnotation(_BaseAnnotation):
    """Class for parsing the "annotations" key of a job response for named entities recognition."""

    @staticmethod
    def _get_compatible_ml_task() -> Literal["NAMED_ENTITIES_RECOGNITION"]:
        return "NAMED_ENTITIES_RECOGNITION"

    @property
    def begin_offset(self) -> int:
        """Returns the begin offset of the annotation."""
        return self.json_data["beginOffset"]

    @property
    def end_offset(self) -> int:
        """Returns the end offset of the annotation."""
        return self.json_data["endOffset"]

    @property
    def content(self) -> str:
        """Returns the content of the annotation."""
        return self.json_data["content"]


class _BaseAnnotationWithTool(_BaseAnnotation):
    """Base class for annotations with a "type" key (tool used to create the annotation)."""

    @property
    def type(self) -> str:
        """Returns the tool of the annotation.

        One of: "rectangle", "polygon", or "semantic".
        """
        return self.json_data["type"]


class PointAnnotation(_BaseAnnotationWithTool):
    """Class for parsing the "annotations" key of a job response for 1D object detection jobs."""

    @staticmethod
    def _get_compatible_ml_task() -> Literal["OBJECT_DETECTION"]:
        return "OBJECT_DETECTION"

    @staticmethod
    def _get_compatible_type_of_tools() -> Sequence[Literal["marker"]]:
        return ("marker",)

    @property
    def point(self) -> Dict:
        """Returns the point of a point detection job."""
        return self.json_data["point"]


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
    def bounding_poly(self) -> BoundingPoly:
        """Returns the polygon of the object contour."""
        self.json_data["boundingPoly"][0] = BoundingPoly(
            self.json_data["boundingPoly"][0], job_interface=self.job_interface
        )
        return self.json_data["boundingPoly"][0]

    @property
    def score(self) -> int:
        """Returns the score which is the confidence of the object detection.

        Useful when a pre-annotation model is used.
        """
        return self.json_data["score"]


class BoundingPolyAnnotation(_Base2DAnnotation):
    """Class for parsing the "annotations" key of a job response for 2D object detection jobs."""


class VideoAnnotation(_Base2DAnnotation):
    """Class for parsing the "annotations" key of a job response for video object detection jobs."""

    @property
    def is_key_frame(self) -> bool:
        """Returns a boolean indicating if the timestamp or frame is used for interpolation."""
        try:
            return self.json_data["isKeyFrame"]
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
    def kind(self) -> str:
        """Returns the job kind. In pose estimation jobs, this is always "POSE_ESTIMATION"."""
        return self.json_data["kind"]

    @property
    def points(self) -> List[Dict]:
        """Returns the list of the points composing the object."""
        return self.json_data["points"]


def check_attribute_compatible_with_job(func):
    """Raises an error if the decorated method is not compatible with the job."""

    @functools.wraps(func)
    # pylint: disable=protected-access
    def wrapper(self, *args, **kwargs):
        attribute_name = func.__name__

        if attribute_name not in self._valid_attributes_for_ml_task[self.job_interface["mlTask"]]:
            raise AttributeNotCompatibleWithJobError(attribute_name)

        if (
            "type" in self.json_data
            and attribute_name not in self._valid_attributes_for_tool[self.json_data["type"]]
        ):
            raise AttributeNotCompatibleWithJobError(attribute_name)

        return func(self, *args, **kwargs)

    return wrapper


@for_all_properties(check_attribute_compatible_with_job)
# pylint: disable=too-many-ancestors
class Annotation(
    EntityAnnotation,
    PointAnnotation,
    BoundingPolyAnnotation,
    VideoAnnotation,
    PoseEstimationAnnotation,
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
        super().__init__(json_data, job_interface=job_interface)

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
