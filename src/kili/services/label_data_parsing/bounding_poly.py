"""Module for the "boundingPoly" key parsing of an object detection job response."""

from typing import Dict, List


class BoundingPoly(Dict):
    """Class for parsing the "boundingPoly" key of an object detection job response."""

    def __init__(self, bounding_poly_json: Dict, job_interface: Dict) -> None:
        """Class for BoundingPoly parsing."""
        super().__init__(bounding_poly_json)

        self.job_interface = job_interface

    @property
    def normalized_vertices(self) -> List:
        """Returns the normalized vertices of the bounding polygon."""
        return self["normalizedVertices"]
