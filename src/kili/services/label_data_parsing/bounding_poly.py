"""Module for the "boundingPoly" key parsing of an object detection job response."""

from typing import Dict, List

from typeguard import typechecked


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

    @property
    def normalized_vertices(self) -> List[Dict[str, float]]:
        """Returns the normalized vertices of the bounding polygon."""
        return self._json_data["normalizedVertices"]

    @normalized_vertices.setter
    @typechecked
    def normalized_vertices(self, normalized_vertices: List[Dict[str, float]]) -> None:
        """Sets the normalized vertices of the bounding polygon."""
        self._json_data["normalizedVertices"] = normalized_vertices


# class BoundingPolyList:
#     """Class for parsing the "boundingPoly" key of an object detection job response."""

#     def __init__(self, job_interface: Dict, bounding_poly_list: List[Dict]) -> None:
#         """Class for parsing the "boundingPoly" key of an object detection job response.

#         Args:
#             bounding_poly_list: List of dicts representing bounding polygons.
#             job_interface: Job interface of the job.
#         """
#         self._job_interface = job_interface

#         self._json_data = []

#         for bounding_poly_dict in bounding_poly_list:
#             self._json_data.append(BoundingPoly(bounding_poly_dict, job_interface=job_interface))

#     def __getitem__(self, index: int) -> BoundingPoly:
#         """Returns the boundingPoly object at the given index.

#         Used for type checking.
#         """
#         return self._json_data[index]
