# Feature is still under development and is not yet suitable for use by general users.
"""Classes for job response parsing."""

from datetime import datetime
from typing import Dict, List, Optional, cast

from typeguard import typechecked

from kili.services.label_data_parsing import annotation as annotation_module
from kili.services.label_data_parsing import category as category_module
from kili.services.types import Job

from .exceptions import AttributeNotCompatibleWithJobError, InvalidMutationError
from .types import Project


class JobPayload:
    """Class for job payload parsing."""

    def __init__(self, job_name: str, project_info: Project, job_payload: Dict) -> None:
        """Class for job payload parsing.

        Args:
            job_name: Name of the job.
            project_info: Information about the project.
            job_payload: Value of the key "job_name" of the job response.
        """
        self._job_name = job_name
        self._project_info = project_info
        self._json_data = job_payload

        self._job_interface = project_info["jsonInterface"][job_name]  # type: ignore

        # cast lists to objects
        if "categories" in self._json_data:
            self._json_data["categories"] = category_module.CategoryList(
                job_name=self._job_name,
                project_info=self._project_info,
                categories_list=self._json_data["categories"],
            )

        if "annotations" in self._json_data:
            self._json_data["annotations"] = annotation_module.AnnotationList(
                job_name=self._job_name,
                project_info=self._project_info,
                annotations_list=self._json_data["annotations"],
            )

    def to_dict(self) -> Dict:
        """Returns the parsed job payload as a dict."""
        ret = {k: v for k, v in self._json_data.items() if k not in ("categories", "annotations")}

        # cast back to python native types
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

    def __repr__(self) -> str:
        """Returns the parsed job payload representation as a string."""
        return repr(self.to_dict())

    def __str__(self) -> str:
        """Returns the parsed job payload as a string."""
        return str(self.to_dict())

    @property
    def categories(self) -> "category_module.CategoryList":
        """Returns a list of Category objects for a classification job."""
        if self._job_interface["mlTask"] != "CLASSIFICATION":
            raise AttributeNotCompatibleWithJobError("categories")

        if "categories" not in self._json_data and not self._job_interface["required"]:
            return category_module.CategoryList(
                categories_list=[], project_info=self._project_info, job_name=self._job_name
            )

        return self._json_data["categories"]

    @property
    def category(self) -> "category_module.Category":
        """Returns a Category object for a classification job if there is only one category.

        Else raises an error.
        """
        if self._job_interface["mlTask"] != "CLASSIFICATION":
            raise AttributeNotCompatibleWithJobError("category")

        if self._job_interface["content"]["input"] not in ("radio", "singleDropdown"):
            raise AttributeNotCompatibleWithJobError("category")

        if "categories" not in self._json_data and not self._job_interface["required"]:
            return None  # type: ignore

        if len(self._json_data["categories"]) != 1:
            raise ValueError(f"Expected 1 category, got {self._json_data['categories']}")

        return self._json_data["categories"][0]

    @typechecked
    def add_category(self, name: str, confidence: Optional[int] = None) -> None:
        """Adds a category to a job with categories."""
        if self._job_interface["mlTask"] != "CLASSIFICATION":
            raise AttributeNotCompatibleWithJobError("add_category")

        if "categories" not in self._json_data:
            category_list = category_module.CategoryList(
                categories_list=[], project_info=self._project_info, job_name=self._job_name
            )
            category_list.add_category(name=name, confidence=confidence)
            self._json_data["categories"] = category_list
        else:
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

        transcription_field_type = self._job_interface["content"]["input"]

        if transcription_field_type == "date":
            try:
                datetime.strptime(text, r"%Y-%m-%d")
            except ValueError as err:
                raise InvalidMutationError(f"Expected a date, got {text}") from err

        elif transcription_field_type == "number" and not text.isnumeric():
            raise InvalidMutationError(f"Expected a number, got {text}")

        self._json_data["text"] = text

    @property
    def is_key_frame(self) -> bool:
        """Returns the value of the key frame for a video classification job."""
        if self._job_interface["mlTask"] != "CLASSIFICATION":
            raise AttributeNotCompatibleWithJobError("is_key_frame")
        return self._json_data["isKeyFrame"]

    @is_key_frame.setter
    @typechecked
    def is_key_frame(self, is_key_frame: bool) -> None:
        """Sets the value of the key frame for a video classification job."""
        if self._job_interface["mlTask"] != "CLASSIFICATION":
            raise AttributeNotCompatibleWithJobError("is_key_frame")
        self._json_data["isKeyFrame"] = is_key_frame

    @property
    def annotations(self) -> "annotation_module.AnnotationList":
        """Returns a list of Annotation objects for a job."""
        if not _can_query_annotations(json_data=self._json_data, job_interface=self._job_interface):
            raise AttributeNotCompatibleWithJobError("annotations")

        if "annotations" not in self._json_data and not self._job_interface["required"]:
            return annotation_module.AnnotationList(
                annotations_list=[], project_info=self._project_info, job_name=self._job_name
            )

        return self._json_data["annotations"]

    @property
    def entity_annotations(self) -> List["annotation_module.EntityAnnotation"]:
        """Returns a list of EntityAnnotation objects for a named entities recognition job."""
        if self._job_interface["mlTask"] != "NAMED_ENTITIES_RECOGNITION":
            raise AttributeNotCompatibleWithJobError("entity_annotations")

        if not _can_query_annotations(json_data=self._json_data, job_interface=self._job_interface):
            raise AttributeNotCompatibleWithJobError("entity_annotations")

        return cast(List["annotation_module.EntityAnnotation"], self._json_data["annotations"])

    @property
    def bounding_poly_annotations(self) -> List["annotation_module.BoundingPolyAnnotation"]:
        """Returns a list of BoundingPolyAnnotation objects for an object detection job."""
        if self._job_interface["mlTask"] != "OBJECT_DETECTION":
            raise AttributeNotCompatibleWithJobError("bounding_poly_annotations")

        if not _can_query_annotations(json_data=self._json_data, job_interface=self._job_interface):
            raise AttributeNotCompatibleWithJobError("bounding_poly_annotations")

        return cast(
            List["annotation_module.BoundingPolyAnnotation"], self._json_data["annotations"]
        )

    @typechecked
    def add_annotation(self, annotation_dict: Dict) -> None:
        """Adds an annotation to a job with annotations."""
        if not _can_query_annotations(json_data=self._json_data, job_interface=self._job_interface):
            raise AttributeNotCompatibleWithJobError("add_annotation")

        if "annotations" not in self._json_data:
            annotation_list = annotation_module.AnnotationList(
                annotations_list=[], project_info=self._project_info, job_name=self._job_name
            )
            annotation_list.add_annotation(annotation_dict)
            self._json_data["annotations"] = annotation_list
        else:
            self._json_data["annotations"].add_annotation(annotation_dict)


def _can_query_annotations(json_data: Dict, job_interface: Job) -> bool:
    """Checks if the "annotations" key can be queried for the job."""
    if "annotations" in json_data:
        return True

    if job_interface["mlTask"] in ("CLASSIFICATION",):
        return False

    if not job_interface["required"]:
        return True

    return True
