# Feature is still under development and is not yet suitable for use by general users.
"""Module for the "categories" key parsing of a job response."""
from typing import Dict, List

from typeguard import typechecked

from .exceptions import InvalidMutationError


class Category(Dict):
    """Class for Category parsing."""

    def __init__(self, job_interface: Dict, name: str, confidence: int = 100) -> None:
        """Class for Category parsing.

        Args:
            name: Name of the category label.
            confidence: Confidence of the category label.
            job_interface: Job interface of the job.
        """
        super().__init__()
        self.job_interface = job_interface

        self.name = name
        self.confidence = confidence

    @property
    def name(self) -> str:
        """Returns the name of the category label."""
        return self["name"]

    @name.setter
    @typechecked
    def name(self, name: str) -> None:
        """Sets the name of the category label."""
        if name not in self.job_interface["content"]["categories"]:
            raise InvalidMutationError(
                f"Category {name} is not in the job interface categories"
                f" {self.job_interface['content']['categories'].keys()}"
            )
        self["name"] = name

    @property
    def confidence(self) -> int:
        """Returns the confidence of the category label."""
        return self["confidence"]

    @confidence.setter
    @typechecked
    def confidence(self, confidence: int) -> None:
        """Sets the confidence of the category label."""
        if not 0 <= confidence <= 100:
            raise ValueError(f"Confidence must be between 0 and 100, got {confidence}")
        self["confidence"] = confidence


class CategoryList(List):
    """Class for the categories list parsing."""

    def __init__(self, job_interface: Dict, categories_list: List[Dict]) -> None:
        """Class for the categories list parsing.

        Args:
            categories_list: List of dicts representing categories.
            job_interface: Job interface of the job.
        """
        super().__init__()
        self.job_interface = job_interface

        for category_dict in categories_list:
            self.append(Category(**category_dict, job_interface=job_interface))

    def _check_can_append_category(self) -> None:
        input_type = self.job_interface["content"]["input"]
        nb_classes = len(self.job_interface["content"]["categories"])
        len_categories = len(self)

        if input_type == "radio":
            if len_categories >= 1:
                raise InvalidMutationError(
                    "Cannot add more than one category to a radio button classification job."
                )

        elif input_type == "checkbox":
            if len_categories >= nb_classes:
                raise InvalidMutationError(
                    "Cannot add more categories than the number of classes to a checkbox"
                    " classification job."
                )

        elif input_type == "singleDropdown":
            if len_categories >= 1:
                raise InvalidMutationError(
                    "Cannot add more than one category to a single dropdown classification job."
                )

        elif input_type == "multipleDropdown":
            if len_categories >= nb_classes:
                raise InvalidMutationError(
                    "Cannot add more categories than the number of classes to a multiple dropdown"
                    " classification job."
                )

        else:
            raise ValueError(f"Invalid input type: {input_type}")

    @typechecked
    def append(self, category: Category) -> None:
        """Appends a category object to the CategoryList object."""
        self._check_can_append_category()
        return super().append(category)
