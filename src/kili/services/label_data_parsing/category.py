# Feature is still under development and is not yet suitable for use by general users.
"""Module for the "categories" key parsing of a job response."""
from typing import Any, Dict, List, Optional

from typeguard import typechecked

from .exceptions import InvalidMutationError


class Category:
    """Class for Category parsing."""

    def __init__(self, category_json: Dict, job_interface: Dict) -> None:
        """Class for Category parsing.

        Args:
            category_json: Value of the key "categories".
            job_interface: Job interface of the job.
        """
        self._json_data = {}
        self._job_interface = job_interface

        self.name = category_json["name"]
        if "confidence" in category_json:
            self.confidence = category_json["confidence"]
        if "children" in category_json:
            self.children = category_json["children"]

    def __str__(self) -> str:
        """Returns the string representation of the category."""
        return str(self._json_data)

    def __repr__(self) -> str:
        """Returns the string representation of the category."""
        return repr(self._json_data)

    def as_dict(self) -> Dict:
        """Returns the parsed category as a dict."""
        return self._json_data

    @property
    def name(self) -> str:
        """Returns the name of the category label."""
        return self._json_data["name"]

    @name.setter
    @typechecked
    def name(self, name: str) -> None:
        """Sets the name of the category label."""
        if name not in self._job_interface["content"]["categories"]:
            raise InvalidMutationError(
                f"Category '{name}' is not in the job interface with categories:"
                f" {self._job_interface['content']['categories'].keys()}"
            )
        self._json_data["name"] = name

    @property
    def confidence(self) -> int:
        """Returns the confidence of the category label."""
        return self._json_data["confidence"]

    @confidence.setter
    @typechecked
    def confidence(self, confidence: int) -> None:
        """Sets the confidence of the category label."""
        if not 0 <= confidence <= 100:
            raise ValueError(f"Confidence must be between 0 and 100, got {confidence}")
        self._json_data["confidence"] = confidence

    @property
    def children(self):
        """Returns the children of the category label."""
        return self._json_data["children"]

    @children.setter
    @typechecked
    def children(self, children: List[Dict[str, Any]]) -> None:
        """Sets the children of the category label."""
        self._json_data["children"] = children


class CategoryList:
    """Class for the categories list parsing."""

    def __init__(self, categories_list: List[Dict[str, Any]], job_interface: Dict) -> None:
        """Class for the categories list parsing.

        Args:
            categories_list: List of dicts representing categories.
            job_interface: Job interface of the job.
        """
        self._categories_list: List[Category] = []
        self._job_interface = job_interface

        for category_dict in categories_list:
            self.add_category(**category_dict)

    def _check_can_append_category(self, category: Category) -> None:
        input_type = self._job_interface["content"]["input"]
        nb_classes = len(self._job_interface["content"]["categories"])
        len_categories = len(self._categories_list)

        if input_type in ("radio", "singleDropdown"):
            if len_categories >= 1:
                raise InvalidMutationError(
                    f"Cannot add more than one category to a {input_type} classification job."
                )

        elif input_type in ("checkbox", "multipleDropdown"):
            if len_categories >= nb_classes:
                raise InvalidMutationError(
                    f"Cannot add more categories than the number of classes to a {input_type}"
                    " classification job."
                )

        else:
            raise ValueError(f"Invalid input type: {input_type}")

        # Check that the name of the category we want to add is not already in the list
        if any(category.name == cat.name for cat in self._categories_list):
            raise InvalidMutationError(
                f"Cannot add a category with name '{category.name}' because a category with the"
                f" same name already exists: {self._categories_list}"
            )

    @typechecked
    def add_category(self, name: str, confidence: Optional[int] = None) -> None:
        """Adds a category object to the CategoryList object."""
        category_dict: Dict[str, object] = {"name": name}
        if confidence is not None:
            category_dict["confidence"] = confidence

        category = Category(
            category_json=category_dict,
            job_interface=self._job_interface,
        )
        self._check_can_append_category(category)
        self._categories_list.append(category)

    @typechecked
    def __getitem__(self, index: int) -> Category:
        """Returns the category object at the given index."""
        return self._categories_list[index]

    def __len__(self) -> int:
        """Returns the number of categories."""
        return len(self._categories_list)

    def __str__(self) -> str:
        """Returns the string representation of the categories list."""
        return str(self.as_list())

    def __repr__(self) -> str:
        """Returns the string representation of the categories list."""
        return repr(self.as_list())

    def as_list(self) -> List[Dict]:
        """Returns the list of categories as a list of dicts."""
        return [category.as_dict() for category in self._categories_list]
