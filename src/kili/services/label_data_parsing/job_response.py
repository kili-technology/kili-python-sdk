# Feature is still under development and is not yet suitable for use by general users.
"""Classes for job response parsing."""

from typing import Dict, List

from .annotation import Annotation, BoundingPolyAnnotation, EntityAnnotation
from .category import Category, CategoryList
from .exceptions import AttributeNotCompatibleWithJobError


class JobPayload:
    """Class for job payload parsing."""

    def __init__(self, job_name: str, job_interface: Dict, job_payload: Dict) -> None:
        """Class for job payload parsing.

        Args:
            job_name: Name of the job.
            job_interface: Job interface of the job.
            job_payload: Value of the key "job_name" of the job response.
        """
        self.job_name = job_name
        self.job_interface = job_interface
        self.json_data = job_payload

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
        """Returns a list of Category objects for a classification job."""
        if self.job_interface["mlTask"] != "CLASSIFICATION":
            raise AttributeNotCompatibleWithJobError("categories")

        if "categories" not in self.json_data and not self.is_required_job:
            self.json_data["categories"] = CategoryList(self.job_interface, [])

        return self.json_data["categories"]

    @property
    def category(self) -> Category:
        """Returns a Category object for a classification job if there is only one category.

        Else raises an error.
        """
        if self.job_interface["mlTask"] != "CLASSIFICATION":
            raise AttributeNotCompatibleWithJobError("category")

        if self.job_interface["content"]["input"] not in ("radio", "singleDropdown"):
            raise AttributeNotCompatibleWithJobError("category")

        if "categories" not in self.json_data and not self.is_required_job:
            return None  # type: ignore

        return self.json_data["categories"][0]

    @property
    def text(self) -> str:
        """Returns the text for a transcription job."""
        if self.job_interface["mlTask"] != "TRANSCRIPTION":
            raise AttributeNotCompatibleWithJobError("text")
        return self.json_data["text"]

    @property
    def annotations(self) -> List[Annotation]:
        """Returns a list of Annotation objects for a job."""
        return [
            Annotation(annotation, self.job_interface)
            for annotation in self.json_data["annotations"]
        ]

    @property
    def entity_annotations(self) -> List[EntityAnnotation]:
        """Returns a list of EntityAnnotation objects for a named entities recognition job."""
        if self.job_interface["mlTask"] != "NAMED_ENTITIES_RECOGNITION":
            raise AttributeNotCompatibleWithJobError("entity_annotations")

        return [
            EntityAnnotation(annotation, self.job_interface)
            for annotation in self.json_data["annotations"]
        ]

    @property
    def bounding_poly_annotations(self) -> List[BoundingPolyAnnotation]:
        """Returns a list of BoundingPolyAnnotation objects for an object detection job."""
        if self.job_interface["mlTask"] != "OBJECT_DETECTION":
            raise AttributeNotCompatibleWithJobError("bounding_poly_annotations")

        return [
            BoundingPolyAnnotation(annotation, self.job_interface)
            for annotation in self.json_data["annotations"]
        ]
