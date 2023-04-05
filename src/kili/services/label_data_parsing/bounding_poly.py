"""Module for the "boundingPoly" key parsing of an object detection job response."""

from typing import Any, Dict, List

from typeguard import typechecked
from typing_extensions import Literal

from .exceptions import InvalidMutationError
from .types import Project


class BoundingPoly:
    """Class for parsing an element of a boundingPoly list."""

    def __init__(self, bounding_poly_json: Dict[Literal["normalizedVertices"], Any]) -> None:
        """Class for BoundingPoly parsing."""
        self._json_data: Dict[Literal["normalizedVertices"], Any] = {}

        self.normalized_vertices = bounding_poly_json["normalizedVertices"]

    def __str__(self) -> str:
        """Returns the string representation of the boundingPoly object."""
        return str(self._json_data)

    def __repr__(self) -> str:
        """Returns the string representation of the boundingPoly object."""
        return repr(self._json_data)

    def as_dict(self) -> Dict:
        """Returns the boundingPoly object as a dict."""
        return self._json_data

    @property
    def normalized_vertices(self) -> List[Dict[Literal["x", "y"], float]]:
        """Returns the normalized vertices of the bounding polygon."""
        return self._json_data["normalizedVertices"]

    @normalized_vertices.setter
    @typechecked
    def normalized_vertices(
        self, normalized_vertices: List[Dict[Literal["x", "y"], float]]
    ) -> None:
        """Sets the normalized vertices of the bounding polygon."""
        for vertex in normalized_vertices:
            if not 0 <= vertex["x"] <= 1:
                raise ValueError(f"Vertex x coordinate with value {vertex['x']} is not in [0, 1].")
            if not 0 <= vertex["y"] <= 1:
                raise ValueError(f"Vertex y coordinate with value {vertex['y']} is not in [0, 1].")
        self._json_data["normalizedVertices"] = normalized_vertices


class BoundingPolyList:
    """Class for the boundingPoly list parsing."""

    def __init__(
        self,
        bounding_poly_list: List[Dict[Literal["normalizedVertices"], Any]],
        project_info: Project,
        job_name: str,
    ) -> None:
        """Class for the boundingPoly list parsing.

        Args:
            bounding_poly_list: List of dicts representing bounding polygons.
            project_info: Information about the project.
            job_name: Name of the job.
        """
        self._bounding_poly_list: List[BoundingPoly] = []
        self._project_info = project_info
        self._job_name = job_name

        self._job_interface = project_info["jsonInterface"][job_name]  # type: ignore

        for bounding_poly_dict in bounding_poly_list:
            self.add_bounding_poly(bounding_poly_dict)

    def _check_can_append_bounding_poly(self, bounding_poly: BoundingPoly) -> None:
        if "normalizedVertices" not in bounding_poly._json_data:  # pylint: disable=protected-access
            raise KeyError("Bounding polygon must have a 'normalizedVertices' key.")
        if self._job_interface["mlTask"] != "OBJECT_DETECTION":
            raise InvalidMutationError(
                "BoundingPolyList can only be mutated for an object detection job."
            )

    @typechecked
    def add_bounding_poly(self, bounding_poly: Dict[Literal["normalizedVertices"], Any]) -> None:
        """Adds a boundingPoly object to a BoundingPolyList object."""
        bounding_poly_obj = BoundingPoly(bounding_poly)
        self._check_can_append_bounding_poly(bounding_poly_obj)
        self._bounding_poly_list.append(bounding_poly_obj)

    @typechecked
    def __getitem__(self, index: int) -> BoundingPoly:
        """Returns the boundingPoly object at the given index."""
        return self._bounding_poly_list[index]

    def __len__(self) -> int:
        """Returns the number of bounding polygons."""
        return len(self._bounding_poly_list)

    def __str__(self) -> str:
        """Returns the string representation of the boundingPoly list."""
        return str(self.as_list())

    def __repr__(self) -> str:
        """Returns the string representation of the boundingPoly list."""
        return repr(self.as_list())

    def as_list(self) -> List[Dict]:
        """Returns the list of bounding polygons as a list of dicts."""
        return [bounding_poly.as_dict() for bounding_poly in self._bounding_poly_list]
