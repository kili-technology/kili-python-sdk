"""Module for the "boundingPoly" key parsing of an object detection job response."""

from typing import Dict, Iterator, List, Literal, Optional, Union

from typeguard import typechecked

from .exceptions import InvalidMutationError
from .types import NormalizedVertex, Project


class BoundingPoly:
    """Class for parsing an element of a boundingPoly list."""

    def __init__(
        self,
        bounding_poly_json: Dict[
            Literal["normalizedVertices"],
            Union[List[NormalizedVertex], List[List[NormalizedVertex]]],
        ],
        type_of_tool: Optional[Literal["rectangle", "polygon", "semantic"]],
    ) -> None:
        """Class for BoundingPoly parsing."""
        self._json_data: Dict[
            Literal["normalizedVertices"],
            Union[List[NormalizedVertex], List[List[NormalizedVertex]]],
        ] = {}
        self._type_of_tool = type_of_tool

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
    def normalized_vertices(
        self,
    ) -> Union[List[NormalizedVertex], List[List[NormalizedVertex]]]:
        """Returns the normalized vertices of the bounding polygon."""
        return self._json_data["normalizedVertices"]

    @normalized_vertices.setter
    @typechecked
    def normalized_vertices(
        self,
        normalized_vertices: Union[List[NormalizedVertex], List[List[NormalizedVertex]]],
    ) -> None:
        """Sets the normalized vertices of the bounding polygon.

        Args:
            normalized_vertices: List of normalized vertices for object detection tasks.
                Or a list of a list of normalized vertices for NER in PDF task.
        """
        # for object detection tasks type of tool is defined
        if self._type_of_tool:
            nb_vertices = len(normalized_vertices)

            if self._type_of_tool == "rectangle" and nb_vertices != 4:
                raise InvalidMutationError(
                    f"Bounding polygon with {nb_vertices} vertices is not a rectangle."
                )

            if self._type_of_tool == "polygon" and nb_vertices < 3:
                raise InvalidMutationError(
                    f"Bounding polygon with {nb_vertices} vertices is not a polygon."
                )

        vertices = normalized_vertices if self._type_of_tool else normalized_vertices[0]
        for vertex in vertices:
            assert isinstance(vertex, dict), f"Vertex {vertex} is not a dict."

        self._json_data["normalizedVertices"] = normalized_vertices


class BoundingPolyList:
    """Class for the boundingPoly list parsing."""

    def __init__(
        self,
        bounding_poly_list: List[
            Dict[
                Literal["normalizedVertices"],
                Union[List[NormalizedVertex], List[List[NormalizedVertex]]],
            ]
        ],
        project_info: Project,
        job_name: str,
        type_of_tool: Optional[Literal["rectangle", "polygon", "semantic"]],
    ) -> None:
        """Class for the boundingPoly list parsing.

        Args:
            bounding_poly_list: List of dicts representing bounding polygons.
            project_info: Information about the project.
            job_name: Name of the job.
            type_of_tool: Type of tool used to create the bounding poly instances.
        """
        self._bounding_poly_list: List[BoundingPoly] = []
        self._project_info = project_info
        self._job_name = job_name
        self._type_of_tool: Optional[Literal["rectangle", "polygon", "semantic"]] = type_of_tool

        self._job_interface = project_info["jsonInterface"][job_name]  # type: ignore

        for bounding_poly_dict in bounding_poly_list:
            self.add_bounding_poly(bounding_poly_dict)

    def _check_can_append_bounding_poly(self, bounding_poly: BoundingPoly) -> None:
        if "normalizedVertices" not in bounding_poly._json_data:  # pylint: disable=protected-access
            raise KeyError("Bounding polygon must have a 'normalizedVertices' key.")

        if self._job_interface["mlTask"] not in ("OBJECT_DETECTION", "NAMED_ENTITIES_RECOGNITION"):
            raise InvalidMutationError(
                "BoundingPolyList can only be mutated for an object detection or NER in PDF jobs."
            )

    @typechecked
    def add_bounding_poly(
        self,
        bounding_poly: Dict[
            Literal["normalizedVertices"],
            Union[List[NormalizedVertex], List[List[NormalizedVertex]]],
        ],
    ) -> None:
        """Adds a boundingPoly object to a BoundingPolyList object."""
        bounding_poly_obj = BoundingPoly(bounding_poly, type_of_tool=self._type_of_tool)
        self._check_can_append_bounding_poly(bounding_poly_obj)
        self._bounding_poly_list.append(bounding_poly_obj)

    @typechecked
    def __getitem__(self, index: int) -> BoundingPoly:
        """Returns the boundingPoly object at the given index."""
        return self._bounding_poly_list[index]

    def __len__(self) -> int:
        """Returns the number of bounding polygons."""
        return len(self._bounding_poly_list)

    def __iter__(self) -> Iterator[BoundingPoly]:
        """Allows iterating over the boundingPoly list."""
        return iter(self._bounding_poly_list)

    def __str__(self) -> str:
        """Returns the string representation of the boundingPoly list."""
        return str(self.as_list())

    def __repr__(self) -> str:
        """Returns the string representation of the boundingPoly list."""
        return repr(self.as_list())

    def as_list(self) -> List[Dict]:
        """Returns the list of bounding polygons as a list of dicts."""
        return [bounding_poly.as_dict() for bounding_poly in self._bounding_poly_list]
