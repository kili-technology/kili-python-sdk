"""Utilities to handle assets."""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class PageResolution:
    """A wrapper for PageResolution GraphQL object."""

    width: float
    height: float
    page_number: int
    rotation: int = 0

    def as_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the object."""
        output = {
            "width": self.width,
            "height": self.height,
            "pageNumber": self.page_number,
        }
        if self.rotation != 0:
            output["rotation"] = self.rotation

        return output
