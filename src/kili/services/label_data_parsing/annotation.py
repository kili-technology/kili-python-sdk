"""Module for the "annotations" key parsing of a job response."""

import functools
from collections import defaultdict
from typing import Dict, Iterator, List, Literal, Optional, Sequence, Union

from typeguard import typechecked

from kili.services.label_data_parsing import category as category_module
from kili.services.label_data_parsing import json_response as json_response_module

from .bounding_poly import BoundingPolyList
from .decorators import for_all_properties
from .exceptions import AttributeNotCompatibleWithJobError, InvalidMutationError
from .types import NormalizedVertex, Project
from .utils import get_children_job_names


class _BaseAnnotation:
    """Class for parsing the "annotations" key of a job response.

    It is used as a base class for the common properties of all types of annotations.
    """

    def __init__(self, annotation_json: Dict, project_info: Project, job_name: str) -> None:
        """Class for Annotation parsing.

        Args:
            annotation_json: Dict of an annotation. It is the value of
                the "annotations" key of a job response.
            project_info: Information about the project.
            job_name: Name of the job.
        """
        self._json_data = annotation_json
        self._project_info = project_info
        self._job_name = job_name

        self._job_interface = project_info["jsonInterface"][job_name]  # type: ignore

        # cast lists to objects
        if "categories" in self._json_data and isinstance(self._json_data["categories"], List):
            self._json_data["categories"] = category_module.CategoryList(
                categories_list=self._json_data["categories"],
                project_info=self._project_info,
                job_name=self._job_name,
            )
        if "boundingPoly" in self._json_data and isinstance(self._json_data["boundingPoly"], List):
            self._json_data["boundingPoly"] = BoundingPolyList(
                bounding_poly_list=self._json_data["boundingPoly"],
                project_info=self._project_info,
                job_name=self._job_name,
                type_of_tool=self._json_data.get("type"),
            )
        if "points" in self._json_data and isinstance(self._json_data["points"], List):
            self._json_data["points"] = [
                PoseEstimationPointAnnotation(
                    project_info=self._project_info, job_name=self._job_name, annotation_json=point
                )
                for point in self._json_data["points"]
            ]
        if self._json_data.get("children"):
            self.children = self._json_data["children"]  # call children setter

    def __str__(self) -> str:
        return str(self._json_data)

    def __repr__(self) -> str:
        return repr(self._json_data)

    def as_dict(self) -> Dict:
        """Return the parsed annotation as a dict."""
        ret = {
            k: v
            for k, v in self._json_data.items()
            if k not in ("categories", "children", "boundingPoly", "points")
        }
        if "categories" in self._json_data:
            ret["categories"] = (
                self._json_data["categories"]
                if isinstance(self._json_data["categories"], List)
                else self._json_data["categories"].as_list()
            )
        if "boundingPoly" in self._json_data:
            ret["boundingPoly"] = (
                self._json_data["boundingPoly"]
                if isinstance(self._json_data["boundingPoly"], List)
                else self._json_data["boundingPoly"].as_list()
            )
        if "points" in self._json_data:
            ret["points"] = [point.as_dict() for point in self._json_data["points"]]
        if "children" in self._json_data:
            ret["children"] = (
                self._json_data["children"].to_dict()
                if not isinstance(self._json_data["children"], Dict)
                else self._json_data["children"]
            )
        return ret

    @property
    def categories(self) -> "category_module.CategoryList":
        """Returns the list of categories of the annotation."""
        return self._json_data["categories"]

    @property
    def category(self) -> "category_module.Category":
        """Returns the category of the annotation if there is only one category.

        Else raises an error.
        """
        if self._job_interface["content"]["input"] not in ("radio", "singleDropdown"):
            raise AttributeNotCompatibleWithJobError("category")

        if "categories" not in self._json_data and not self._job_interface["required"]:
            return None  # type: ignore

        if len(self._json_data["categories"]) != 1:
            raise ValueError(f"Expected 1 category, got {self._json_data['categories']}")

        return self._json_data["categories"][0]

    @typechecked
    def add_category(self, name: str, confidence: Optional[float] = None) -> None:
        """Add a category to an annotation job with categories."""
        if "categories" not in self._json_data:
            category_list = category_module.CategoryList(
                categories_list=[], project_info=self._project_info, job_name=self._job_name
            )
            category_list.add_category(name=name, confidence=confidence)
            self._json_data["categories"] = category_list
        else:
            self._json_data["categories"].add_category(name=name, confidence=confidence)

    @property
    def mid(self) -> str:
        """Returns the annotation unique identifier."""
        return self._json_data["mid"]

    @mid.setter
    @typechecked
    def mid(self, mid: str) -> None:
        """Set the annotation unique identifier."""
        if len(mid) == 0:
            raise ValueError("mid must be non-empty.")
        self._json_data["mid"] = mid

    @property
    def children(self) -> "json_response_module.ParsedJobs":
        """Returns the parsed children jobs of the job."""
        return self._json_data["children"]

    @children.setter
    @typechecked
    def children(self, children: Dict) -> None:
        """Set the children jobs of the annotation job."""
        job_names_to_parse = get_children_job_names(
            json_interface=self._project_info["jsonInterface"],
            job_interface=self._job_interface,  # type: ignore
        )
        parsed_children_job = json_response_module.ParsedJobs(
            project_info=self._project_info,
            json_response=children,
            job_names_to_parse=job_names_to_parse,
        )
        self._json_data["children"] = parsed_children_job


class _BaseNamedEntityRecognitionAnnotation(_BaseAnnotation):
    """Base class for parsing the "content" key of an annotation for NER job response.

    Either simple NER or NER in PDFs.
    """

    @property
    def content(self) -> str:
        """Returns the content of the annotation."""
        return self._json_data["content"]

    @content.setter
    @typechecked
    def content(self, content: str) -> None:
        """Set the content of the annotation."""
        self._json_data["content"] = content


class EntityAnnotation(_BaseNamedEntityRecognitionAnnotation):
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
        """Set the begin offset of the annotation."""
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
        """Set the end offset of the annotation."""
        if end_offset < 0:
            raise ValueError(f"end_offset must be positive, got {end_offset}")
        self._json_data["endOffset"] = end_offset


class _BaseAnnotationWithTool(_BaseAnnotation):
    """Base class for annotations with a "type" key (tool used to create the annotation)."""

    @property
    def type(
        self,
    ) -> Literal["rectangle", "polygon", "semantic", "marker", "vector", "polyline", "pose"]:
        """Returns the tool of the annotation."""
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
    def point(self) -> NormalizedVertex:
        """Returns the point of a point detection job."""
        return self._json_data["point"]

    @point.setter
    @typechecked
    def point(self, point: NormalizedVertex) -> None:
        """Set the point of a point detection job."""
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
    def polyline(self) -> List[NormalizedVertex]:
        """Returns the polyline of a polyline detection job."""
        return self._json_data["polyline"]

    @polyline.setter
    @typechecked
    def polyline(self, polyline: List[NormalizedVertex]) -> None:
        """Set the polyline of a polyline detection job."""
        self._json_data["polyline"] = polyline


class _BaseAnnotationWithBoundingPoly(_BaseAnnotation):
    """Base class for annotations with a "boundingPoly" key."""

    @property
    def bounding_poly(self) -> BoundingPolyList:
        """Returns the polygon of the object contour."""
        return self._json_data["boundingPoly"]


# pylint: disable=line-too-long
class EntityInPdfAnnotation(_BaseNamedEntityRecognitionAnnotation, _BaseAnnotationWithBoundingPoly):
    """Class for parsing the "annotations" key of a job response for named entities recognition in PDFs."""

    @staticmethod
    def _get_compatible_ml_task() -> Literal["NAMED_ENTITIES_RECOGNITION"]:
        return "NAMED_ENTITIES_RECOGNITION"

    @property
    def annotations(self) -> "AnnotationList":
        """Return the tist of positions of the annotation.

        For NER, when an annotation spans multiple lines, there will be multiple polys and a single boundingPoly.
        """
        return AnnotationList(
            job_name=self._job_name,
            project_info=self._project_info,
            annotations_list=self._json_data["annotations"],
        )

    @property
    def polys(
        self,
    ) -> List[Dict[Literal["normalizedVertices"], List[List[NormalizedVertex]]]]:
        """Return the coordinates from the different rectangles in the annotation.

        An annotation can have several rectangles (for example if the annotation covers more than one line).
        """
        return self._json_data["polys"]

    @property
    def page_number_array(self) -> List[int]:
        """Return the pages where the annotation appears."""
        return self._json_data["pageNumberArray"]


class _Base2DAnnotation(_BaseAnnotationWithTool, _BaseAnnotationWithBoundingPoly):
    """Base class for 2D annotations."""

    @staticmethod
    def _get_compatible_ml_task() -> Literal["OBJECT_DETECTION"]:
        return "OBJECT_DETECTION"

    @staticmethod
    def _get_compatible_type_of_tools() -> (
        Sequence[Literal["rectangle", "polygon", "semantic", "polyline", "vector"]]
    ):
        return ("rectangle", "polygon", "semantic", "polyline", "vector")

    def add_bounding_poly(
        self,
        bounding_poly_dict: Dict[
            Literal["normalizedVertices"],
            Union[List[NormalizedVertex], List[List[NormalizedVertex]]],
        ],
    ) -> None:
        """Add a bounding polygon to the boundingPoly list."""
        bounding_poly_list = (
            BoundingPolyList(
                bounding_poly_list=[],
                project_info=self._project_info,
                job_name=self._job_name,
                type_of_tool=self._json_data["type"],
            )
            if "boundingPoly" not in self._json_data
            else self._json_data["boundingPoly"]
        )
        bounding_poly_list.add_bounding_poly(bounding_poly_dict)
        self._json_data["boundingPoly"] = bounding_poly_list

    @property
    def score(self) -> Optional[int]:
        """Returns the score which is the confidence of the object detection.

        Available when a pre-annotation model is used.
        """
        return self._json_data.get("score")

    @score.setter
    @typechecked
    def score(self, score: int) -> None:
        """Set the score of the annotation."""
        if not 0 <= score <= 100:
            raise ValueError(f"Score must be between 0 and 100, got {score}.")
        self._json_data["score"] = score


class BoundingPolyAnnotation(_Base2DAnnotation):
    """Class for parsing the "annotations" key of a job response for 2D object detection jobs."""


class VideoAnnotation(_Base2DAnnotation):
    """Class for parsing the "annotations" key of a job response for video object detection jobs."""

    @property
    def is_key_frame(self) -> bool:
        """Returns the value of isKeyFrame for a video job.

        This is a Boolean indicating if the timestamp or frame is used for interpolation.
        """
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
    def _get_compatible_type_of_tools() -> Sequence[Literal["pose", "marker"]]:
        return ("pose", "marker")

    @property
    def kind(self) -> Literal["POSE_ESTIMATION"]:
        """Returns the job kind.

        In pose estimation jobs, this is always "POSE_ESTIMATION".
        """
        return self._json_data["kind"]

    @property
    def points(self) -> List["PoseEstimationPointAnnotation"]:
        """Returns the list of the points composing the object."""
        return self._json_data["points"]


class PoseEstimationPointAnnotation(PointAnnotation):
    """Class for parsing a point object of a job response for pose estimation jobs."""

    @property
    def point(self) -> Dict[Literal["x", "y"], float]:
        """Returns the coordinates of the point."""
        return self._json_data["point"]

    @property
    def code(self) -> str:
        """Returns the code identifier (unique for each point in an object)."""
        return self._json_data["code"]

    @property
    def name(self) -> str:
        """Returns the name of the point."""
        return self._json_data["name"]

    @property
    def job_name(self) -> str:
        """Returns the annotated point job's name."""
        return self._json_data["jobName"]


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
        """Set the list of the start entities composing the relation."""
        self._json_data["startEntities"] = start_entities

    @property
    def end_entities(self) -> List[Dict[Literal["mid"], str]]:
        """Returns the list of the end entities composing the relation."""
        return self._json_data["endEntities"]

    @end_entities.setter
    @typechecked
    def end_entities(self, end_entities: List[Dict[Literal["mid"], str]]) -> None:
        """Set the list of the end entities composing the relation."""
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
        """Set the list of the start objects composing the relation."""
        self._json_data["startObjects"] = start_objects

    @property
    def end_objects(self) -> List[Dict[Literal["mid"], str]]:
        """Returns the list of the end objects composing the relation."""
        return self._json_data["endObjects"]

    @end_objects.setter
    @typechecked
    def end_objects(self, end_objects: List[Dict[Literal["mid"], str]]) -> None:
        """Set the list of the end objects composing the relation."""
        self._json_data["endObjects"] = end_objects


def check_attribute_compatible_with_job(func):
    """Raise an error if the decorated method is not compatible with the job."""

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
    EntityInPdfAnnotation,
    BoundingPolyAnnotation,
    VideoAnnotation,
    PoseEstimationAnnotation,
    EntityRelationAnnotation,
    ObjectRelationAnnotation,
):
    """Class for parsing the "annotations" key of a job response.

    Contains all attributes that can be found in a job response.
    """

    def __init__(self, json_data: Dict, project_info: Project, job_name: str) -> None:
        """Initialize an Annotation object.

        This class is used to parse the "annotations" key of a job response.

        Args:
            json_data: The json data of the annotation.
            project_info: The project info object.
            job_name: The name of the job.
        """
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
            self._valid_attributes_for_ml_task[ml_task].update(parent_class_properties)  # type: ignore

            try:
                type_of_tools = parent_class._get_compatible_type_of_tools()  # type: ignore
            except AttributeError:
                continue

            for tool in type_of_tools:
                self._valid_attributes_for_tool[tool].update(parent_class_properties)  # type: ignore

        super().__init__(annotation_json=json_data, project_info=project_info, job_name=job_name)

    # all properties should be inherited from the base classes


class AnnotationList:
    """Class for the annotations list parsing."""

    def __init__(self, annotations_list: List[Dict], project_info: Project, job_name: str) -> None:
        """Class for the annotations list parsing.

        Args:
            annotations_list: List of dicts representing annotations.
            project_info: The project info object.
            job_name: The name of the job.
        """
        self._project_info = project_info
        self._job_name = job_name
        self._job_interface = self._project_info["jsonInterface"][self._job_name]  # type: ignore

        self._annotations_list: List[Annotation] = []

        for annotation_dict in annotations_list:
            self.add_annotation(annotation_dict)

    def _check_can_append_annotation(self, annotation: Annotation) -> None:
        # pylint: disable=protected-access
        if (
            "type" in annotation._json_data
            and annotation._json_data["type"] not in self._job_interface["tools"]
        ):
            annotation_tool_type = annotation._json_data["type"]
            job_interface_tools = self._job_interface["tools"]

            # pose estimation jobs are a special case
            # the job interface tools is "pose"
            # but the annotation type is "marker"
            if annotation_tool_type == "marker" and "pose" in job_interface_tools:
                return

            if annotation_tool_type not in job_interface_tools:
                raise InvalidMutationError(
                    f"Annotation of type '{annotation._json_data['type']}' cannot be added to this"
                    f" job with tools {self._job_interface['tools']}"
                )

    @typechecked
    def add_annotation(self, annotation_dict: Dict) -> None:
        """Add an annotation object to the AnnotationList object."""
        annotation = Annotation(
            json_data=annotation_dict, project_info=self._project_info, job_name=self._job_name
        )
        self._check_can_append_annotation(annotation)
        self._annotations_list.append(annotation)

    @typechecked
    def __getitem__(self, index: int) -> Annotation:
        """Return the annotation object at the given index."""
        return self._annotations_list[index]

    def __len__(self) -> int:
        """Return the number of annotations."""
        return len(self._annotations_list)

    def __iter__(self) -> Iterator[Annotation]:
        """Return an iterator over the annotations."""
        return iter(self._annotations_list)

    def __str__(self) -> str:
        """Return the string representation of the annotations list."""
        return str(self.as_list())

    def __repr__(self) -> str:
        """Return the string representation of the annotations list."""
        return repr(self.as_list())

    def as_list(self) -> List[Dict]:
        """Return the list of categories as a list of dicts."""
        return [annotation.as_dict() for annotation in self._annotations_list]
