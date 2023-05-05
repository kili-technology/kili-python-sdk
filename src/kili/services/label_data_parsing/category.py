"""Module for the "categories" key parsing of a job response."""
from typing import Any, Dict, Iterator, List, Optional

from typeguard import typechecked

import kili.services.label_data_parsing.json_response as json_response_module

from .exceptions import InvalidMutationError
from .types import Project
from .utils import get_children_job_names


class Category:
    """Class for Category parsing."""

    def __init__(self, category_json: Dict, project_info: Project, job_name: str) -> None:
        """Class for Category parsing.

        Args:
            category_json: Value of the key "categories".
            project_info: Information about the project.
            job_name: Name of the job.
        """
        self._json_data = {}
        self._project_info = project_info
        self._job_name = job_name
        self._job_interface = project_info["jsonInterface"][job_name]  # type: ignore

        # call the setters to check the values are valid
        self.name = category_json["name"]
        if "confidence" in category_json:
            self.confidence = category_json["confidence"]
        if category_json.get("children"):
            self.children = category_json["children"]

    def __str__(self) -> str:
        """Returns the string representation of the category."""
        return str(self._json_data)

    def __repr__(self) -> str:
        """Returns the string representation of the category."""
        return repr(self._json_data)

    def as_dict(self) -> Dict:
        """Returns the parsed category as a dict."""
        ret = {"name": self._json_data["name"]}
        if "confidence" in self._json_data:
            ret["confidence"] = self._json_data["confidence"]
        if "children" in self._json_data:
            ret["children"] = (
                self._json_data["children"].to_dict()
                if not isinstance(self._json_data["children"], Dict)
                else self._json_data["children"]
            )
        return ret

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
                f" {list(self._job_interface['content']['categories'].keys())}"
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
    def children(self) -> "json_response_module.ParsedJobs":
        """Returns the parsed children jobs of the classification job."""
        return self._json_data["children"]

    @children.setter
    @typechecked
    def children(self, children: Dict) -> None:
        """Sets the children jobs of the classification job."""
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


class CategoryList:
    """Class for the categories list parsing."""

    def __init__(
        self, categories_list: List[Dict[str, Any]], project_info: Project, job_name: str
    ) -> None:
        """Class for the categories list parsing.

        Args:
            categories_list: List of dicts representing categories.
            project_info: Information about the project.
            job_name: Name of the job.
        """
        self._categories_list: List[Category] = []
        self._project_info = project_info
        self._job_name = job_name

        self._job_interface = project_info["jsonInterface"][job_name]  # type: ignore

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

        # Check that the name of the category we want to add is not already in the list
        if any(category.name == cat.name for cat in self._categories_list):
            raise InvalidMutationError(
                f"Cannot add a category with name '{category.name}' because a category with the"
                f" same name already exists: {self._categories_list}"
            )

    @typechecked
    def add_category(
        self, name: str, confidence: Optional[int] = None, children: Optional[Dict] = None
    ) -> None:
        """Adds a category object to the CategoryList object."""
        category_dict: Dict[str, object] = {"name": name}
        if confidence is not None:
            category_dict["confidence"] = confidence
        if children is not None:
            category_dict["children"] = children

        category = Category(
            category_json=category_dict,
            project_info=self._project_info,
            job_name=self._job_name,
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

    def __iter__(self) -> Iterator[Category]:
        """Returns an iterator over the categories."""
        return iter(self._categories_list)

    def __str__(self) -> str:
        """Returns the string representation of the categories list."""
        return str(self.as_list())

    def __repr__(self) -> str:
        """Returns the string representation of the categories list."""
        return repr(self.as_list())

    def as_list(self) -> List[Dict]:
        """Returns the list of categories as a list of dicts."""
        return [category.as_dict() for category in self._categories_list]
