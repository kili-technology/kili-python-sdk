# Feature is still under development and is not yet suitable for use by general users.
"""Classes for job response parsing."""

from typing import Dict, List, cast

from typeguard import typechecked

from .annotation import (
    Annotation,
    AnnotationList,
    BoundingPolyAnnotation,
    EntityAnnotation,
)
from .category import Category, CategoryList
from .exceptions import AttributeNotCompatibleWithJobError


class JobPayload:
    """Class for job payload parsing."""

    def __init__(self, job_interface: Dict, job_payload: Dict) -> None:
        """Class for job payload parsing.

        Args:
            job_interface: Job interface of the job.
            job_payload: Value of the key "job_name" of the job response.
        """
        self._job_interface = job_interface
        self._json_data = job_payload

        self._is_required_job = job_interface["required"]

        self._cast_categories()
        self._cast_annotations()

    def _cast_categories(self) -> None:
        """Casts the categories list of the job payload to CategoryList object."""
        if "categories" not in self._json_data:
            return

        if not isinstance(self._json_data["categories"], CategoryList):
            self._json_data["categories"] = CategoryList(
                job_interface=self._job_interface, categories_list=self._json_data["categories"]
            )

    def _cast_annotations(self) -> None:
        """Casts the annotations list of the job payload to Annotation objects."""
        if "annotations" not in self._json_data:
            return

        if not isinstance(self._json_data["annotations"], AnnotationList):
            self._json_data["annotations"] = AnnotationList(
                job_interface=self._job_interface, annotations_list=self._json_data["annotations"]
            )

    def to_dict(self) -> Dict:
        """Returns the parsed job payload as a dict."""
        ret = {k: v for k, v in self._json_data.items() if k not in ("categories", "annotations")}
        if "categories" in self._json_data:
            ret["categories"] = (
                self._json_data["categories"]
                if isinstance(self._json_data["categories"], List)
                else self._json_data["categories"].as_list()
            )
        if "annotations" in self._json_data:
            ret["annotations"] = (
                self._json_data["annotations"]
                if isinstance(self._json_data["annotations"], List)
                else self._json_data["annotations"].as_list()
            )
        return ret

    @property
    def categories(self) -> CategoryList:
        """Returns a list of Category objects for a classification job."""
        if self._job_interface["mlTask"] != "CLASSIFICATION":
            raise AttributeNotCompatibleWithJobError("categories")

        if "categories" not in self._json_data and not self._is_required_job:
            self._json_data["categories"] = CategoryList(
                job_interface=self._job_interface, categories_list=[]
            )

        return self._json_data["categories"]

    @property
    def category(self) -> Category:
        """Returns a Category object for a classification job if there is only one category.

        Else raises an error.
        """
        if self._job_interface["mlTask"] != "CLASSIFICATION":
            raise AttributeNotCompatibleWithJobError("category")

        if self._job_interface["content"]["input"] not in ("radio", "singleDropdown"):
            raise AttributeNotCompatibleWithJobError("category")

        if "categories" not in self._json_data and not self._is_required_job:
            return None  # type: ignore

        if len(self._json_data["categories"]) != 1:
            raise ValueError(f"Expected 1 category, got {self._json_data['categories']}")

        return self._json_data["categories"][0]

    @typechecked
    def add_category(self, name: str, confidence: int) -> None:
        """Adds a category to a job with categories."""
        if self._job_interface["mlTask"] != "CLASSIFICATION":
            raise AttributeNotCompatibleWithJobError("add_category")

        if "categories" not in self._json_data:
            self._json_data["categories"] = CategoryList(
                job_interface=self._job_interface, categories_list=[]
            )

        self._json_data["categories"].add_category(name=name, confidence=confidence)

    @property
    def text(self) -> str:
        """Returns the text for a transcription job."""
        if self._job_interface["mlTask"] != "TRANSCRIPTION":
            raise AttributeNotCompatibleWithJobError("text")
        return self._json_data["text"]

    @text.setter
    @typechecked
    def text(self, text: str) -> None:
        """Sets the text for a transcription job."""
        if self._job_interface["mlTask"] != "TRANSCRIPTION":
            raise AttributeNotCompatibleWithJobError("text")
        self._json_data["text"] = text

    def _can_query_annotations(self) -> bool:
        """Checks if the "annotations" key can be queried for the job."""
        if "annotations" in self._json_data:
            return True

        if self._job_interface["mlTask"] in ("CLASSIFICATION",):
            return False

        if not self._is_required_job:
            return True

        return True

    @property
    def annotations(self) -> List[Annotation]:
        """Returns a list of Annotation objects for a job."""
        if not self._can_query_annotations():
            raise AttributeNotCompatibleWithJobError("annotations")

        return self._json_data.get("annotations", [])

    @property
    def entity_annotations(self) -> List[EntityAnnotation]:
        """Returns a list of EntityAnnotation objects for a named entities recognition job."""
        if self._job_interface["mlTask"] != "NAMED_ENTITIES_RECOGNITION":
            raise AttributeNotCompatibleWithJobError("entity_annotations")

        if not self._can_query_annotations():
            raise AttributeNotCompatibleWithJobError("entity_annotations")

        return cast(List[EntityAnnotation], self._json_data["annotations"])

    @property
    def bounding_poly_annotations(self) -> List[BoundingPolyAnnotation]:
        """Returns a list of BoundingPolyAnnotation objects for an object detection job."""
        if self._job_interface["mlTask"] != "OBJECT_DETECTION":
            raise AttributeNotCompatibleWithJobError("bounding_poly_annotations")

        if not self._can_query_annotations():
            raise AttributeNotCompatibleWithJobError("bounding_poly_annotations")

        return cast(List[BoundingPolyAnnotation], self._json_data["annotations"])

    def add_annotation(self, annotation_dict: Dict) -> None:
        """Adds an annotation to a job with annotations."""
        if not self._can_query_annotations():
            raise AttributeNotCompatibleWithJobError("add_annotation")

        annotation_list = self._json_data["annotations"] or AnnotationList(
            job_interface=self._job_interface, annotations_list=[]
        )
        annotation_list.add_annotation(annotation_dict)
        self._json_data["annotations"] = annotation_list
