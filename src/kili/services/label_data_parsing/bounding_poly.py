"""Module for the "boundingPoly" key parsing of an object detection job response."""

from typing import Dict, List

from typeguard import typechecked
from typing_extensions import Literal


class BoundingPoly:
    """Class for parsing an element of a boundingPoly list."""

    def __init__(self, bounding_poly_json: Dict) -> None:
        """Class for BoundingPoly parsing."""
        self._json_data = bounding_poly_json

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
                raise ValueError(f"Vertex x coordinate {vertex['x']} is not in [0, 1]")
            if not 0 <= vertex["y"] <= 1:
                raise ValueError(f"Vertex y coordinate {vertex['y']} is not in [0, 1]")
        self._json_data["normalizedVertices"] = normalized_vertices
