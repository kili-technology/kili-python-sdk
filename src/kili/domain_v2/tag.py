"""Tag domain contract using TypedDict.

This module provides a TypedDict-based contract for Tag entities,
along with validation utilities and helper functions.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, TypedDict

from typeguard import check_type


class TagContract(TypedDict, total=False):
    """TypedDict contract for Tag entities.

    This contract represents the core structure of a Tag as returned
    from the Kili API. All fields are optional to allow partial data.

    Key fields:
        id: Unique identifier for the tag
        label: Tag label/name
        color: Tag color (hex format)
        organizationId: ID of the organization owning the tag
        checkedForProjects: List of project IDs this tag is assigned to
    """

    id: str
    label: str
    color: str
    organizationId: str
    checkedForProjects: List[str]


def validate_tag(data: Dict[str, Any]) -> TagContract:
    """Validate and return a tag contract.

    Args:
        data: Dictionary to validate as a TagContract

    Returns:
        The validated data as a TagContract

    Raises:
        TypeError: If the data does not match the TagContract structure
    """
    check_type(data, TagContract)
    return data  # type: ignore[return-value]


@dataclass(frozen=True)
class TagView:
    """Read-only view wrapper for TagContract.

    This dataclass provides ergonomic property access to tag data
    while maintaining the underlying dictionary representation.

    Example:
        >>> tag_data = {"id": "123", "label": "important", "color": "#ff0000", ...}
        >>> view = TagView(tag_data)
        >>> print(view.id)
        '123'
        >>> print(view.display_name)
        'important'
    """

    __slots__ = ("_data",)

    _data: TagContract

    @property
    def id(self) -> str:
        """Get tag ID."""
        return self._data.get("id", "")

    @property
    def label(self) -> str:
        """Get tag label."""
        return self._data.get("label", "")

    @property
    def color(self) -> str:
        """Get tag color."""
        return self._data.get("color", "")

    @property
    def organization_id(self) -> str:
        """Get organization ID."""
        return self._data.get("organizationId", "")

    @property
    def checked_for_projects(self) -> List[str]:
        """Get list of project IDs this tag is assigned to."""
        return self._data.get("checkedForProjects", [])

    @property
    def project_count(self) -> int:
        """Get number of projects this tag is assigned to."""
        return len(self.checked_for_projects)

    @property
    def display_name(self) -> str:
        """Get a human-readable display name for the tag.

        Returns the tag label.
        """
        return self.label or self.id

    def to_dict(self) -> TagContract:
        """Get the underlying dictionary representation."""
        return self._data
