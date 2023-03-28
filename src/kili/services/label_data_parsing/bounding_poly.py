"""Module for the "boundingPoly" key parsing of an object detection job response."""

from typing import Dict, List

from typeguard import typechecked


class BoundingPoly(Dict):
    """Class for parsing an element of a boundingPoly list."""

    def __init__(self, bounding_poly_json: Dict, job_interface: Dict) -> None:
        """Class for BoundingPoly parsing."""
        super().__init__(bounding_poly_json)

        self._job_interface = job_interface

    @property
    def normalized_vertices(self) -> List[Dict[str, float]]:
        """Returns the normalized vertices of the bounding polygon."""
        return self["normalizedVertices"]


class BoundingPolyList(List):
    """Class for parsing the "boundingPoly" key of an object detection job response."""

    def __init__(self, job_interface: Dict, bounding_poly_list: List[Dict]) -> None:
        """Class for parsing the "boundingPoly" key of an object detection job response.

        Args:
            bounding_poly_list: List of dicts representing bounding polygons.
            job_interface: Job interface of the job.
        """
        super().__init__()
        self._job_interface = job_interface

        for bounding_poly_dict in bounding_poly_list:
            self.append(BoundingPoly(bounding_poly_dict, job_interface=job_interface))

    @typechecked
    def append(self, bounding_poly: BoundingPoly) -> None:
        """Appends a boundingPoly object to the BoundingPolyList object."""
        return super().append(bounding_poly)

    def __getitem__(self, index: int) -> BoundingPoly:
        """Returns the boundingPoly object at the given index.

        Used for type checking.
        """
        return super().__getitem__(index)
