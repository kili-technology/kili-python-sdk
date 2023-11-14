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
        """Return the string representation of the category."""
        return str(self._json_data)

    def __repr__(self) -> str:
        """Return the string representation of the category."""
        return repr(self._json_data)

    def as_dict(self) -> Dict:
        """Return the parsed category as a dict."""
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
        """Return the name of the category label.

        For a json interface such as:

        ```json
        "CLASSIFICATION_JOB": {
            "mlTask": "CLASSIFICATION",
            "content": {
                "categories": {
                    "CATEGORY_A": {"name": "Category A"},
                    "CATEGORY_B": {"name": "Category B"},
                },
            },
        }
        ```

        The name of the category label can be `CATEGORY_A` or `CATEGORY_B`.

        To get the displayed name of the category label (`Category A`, or `Category B`),
            use the `.display_name` attribute instead.
        """
        return self._json_data["name"]

    @property
    def display_name(self) -> str:
        """Return the displayed name of the category label.

        It is the category name that is displayed in the UI.

        For a json interface such as:

        ```json
        "CLASSIFICATION_JOB": {
            "mlTask": "CLASSIFICATION",
            "content": {
                "categories": {
                    "CATEGORY_A": {"name": "Category A"},
                    "CATEGORY_B": {"name": "Category B"},
                },
            },
        }
        ```

        The displayed name of the category label can be `Category A` or `Category B`.

        To get the name of the category label (`CATEGORY_A` or `CATEGORY_B`),
            use the `.name` attribute instead.
        """
        return self._json_data["display_name"]

    @name.setter
    @typechecked
    def name(self, name: str) -> None:
        """Set the name of the category label."""
        for cat_key, cat_val in self._job_interface["content"]["categories"].items():
            if name == cat_key:
                self._json_data["name"] = name
                self._json_data["display_name"] = cat_val["name"]
                return

        raise InvalidMutationError(
            f"Category '{name}' is not in the job interface with categories:"
            f" {list(self._job_interface['content']['categories'].keys())}"
        )

    @display_name.setter
    @typechecked
    def display_name(self, name: str) -> None:
        """Set the displayed name of the category label."""
        ui_name_to_name = {}
        for cat_key, cat_val in self._job_interface["content"]["categories"].items():
            if cat_val["name"] in ui_name_to_name:
                raise InvalidMutationError(
                    f"Category '{cat_val}' is not unique in the job interface:"
                    f" {self._job_interface}\nUse `.name` instead of `.display_name` to set the"
                    " category name.`"
                )
            ui_name_to_name[cat_val["name"]] = cat_key

        try:
            self._json_data["name"] = ui_name_to_name[name]
            self._json_data["display_name"] = name
        except KeyError as err:
            raise InvalidMutationError(
                f"Category '{name}' is not in the job interface with categories:"
                f" {ui_name_to_name.keys()}"
            ) from err

    @property
    def confidence(self) -> float:
        """Returns the confidence of the category label."""
        return self._json_data["confidence"]

    @confidence.setter
    @typechecked
    def confidence(self, confidence: float) -> None:
        """Set the confidence of the category label."""
        self._json_data["confidence"] = confidence

    @property
    def children(self) -> "json_response_module.ParsedJobs":
        """Returns the parsed children jobs of the classification job."""
        return self._json_data["children"]

    @children.setter
    @typechecked
    def children(self, children: Dict) -> None:
        """Set the children jobs of the classification job."""
        job_names_to_parse = get_children_job_names(
            json_interface=self._project_info["jsonInterface"],
            job_interface=self._job_interface,  # pyright: ignore [reportGeneralTypeIssues]
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

        if input_type in {"radio", "singleDropdown"}:
            if len_categories >= 1:
                raise InvalidMutationError(
                    f"Cannot add more than one category to a {input_type} classification job."
                )

        elif input_type in {"checkbox", "multipleDropdown"} and len_categories >= nb_classes:
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
        self,
        name: str,
        confidence: Optional[float] = None,
        children: Optional[Dict] = None,
    ) -> None:
        """Add a category object to the CategoryList object."""
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
        """Return the category object at the given index."""
        return self._categories_list[index]

    def __len__(self) -> int:
        """Return the number of categories."""
        return len(self._categories_list)

    def __iter__(self) -> Iterator[Category]:
        """Return an iterator over the categories."""
        return iter(self._categories_list)

    def __str__(self) -> str:
        """Return the string representation of the categories list."""
        return str(self.as_list())

    def __repr__(self) -> str:
        """Return the string representation of the categories list."""
        return repr(self.as_list())

    def as_list(self) -> List[Dict]:
        """Return the list of categories as a list of dicts."""
        return [category.as_dict() for category in self._categories_list]
