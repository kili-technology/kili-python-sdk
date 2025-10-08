"""Issue domain contract using TypedDict.

This module provides a TypedDict-based contract for Issue entities,
along with validation utilities and helper functions.
"""

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional, TypedDict

from typeguard import check_type

# Issue types from domain/issue.py
IssueType = Literal["ISSUE", "QUESTION"]
IssueStatus = Literal["CANCELLED", "OPEN", "SOLVED"]


class IssueContract(TypedDict, total=False):
    """TypedDict contract for Issue entities.

    This contract represents the core structure of an Issue as returned
    from the Kili API. All fields are optional to allow partial data.

    Key fields:
        id: Unique identifier for the issue
        createdAt: ISO timestamp of creation
        status: Current status (CANCELLED, OPEN, SOLVED)
        type: Type of issue (ISSUE or QUESTION)
        assetId: ID of the asset this issue is related to
        hasBeenSeen: Whether the issue has been viewed
        objectType: Type of the object (always "Issue")
    """

    id: str
    createdAt: str
    status: IssueStatus
    type: IssueType
    assetId: str
    hasBeenSeen: bool
    objectType: str


def validate_issue(data: Dict[str, Any]) -> IssueContract:
    """Validate and return an issue contract.

    Args:
        data: Dictionary to validate as an IssueContract

    Returns:
        The validated data as an IssueContract

    Raises:
        TypeError: If the data does not match the IssueContract structure
    """
    check_type(data, IssueContract)
    return data  # type: ignore[return-value]


@dataclass(frozen=True)
class IssueView:
    """Read-only view wrapper for IssueContract.

    This dataclass provides ergonomic property access to issue data
    while maintaining the underlying dictionary representation.

    Example:
        >>> issue_data = {"id": "123", "type": "ISSUE", "status": "OPEN", ...}
        >>> view = IssueView(issue_data)
        >>> print(view.id)
        '123'
        >>> print(view.is_open)
        True
    """

    __slots__ = ("_data",)

    _data: IssueContract

    @property
    def id(self) -> str:
        """Get issue ID."""
        return self._data.get("id", "")

    @property
    def created_at(self) -> Optional[str]:
        """Get creation timestamp."""
        return self._data.get("createdAt")

    @property
    def status(self) -> Optional[IssueStatus]:
        """Get issue status."""
        return self._data.get("status")

    @property
    def type(self) -> Optional[IssueType]:
        """Get issue type."""
        return self._data.get("type")

    @property
    def asset_id(self) -> str:
        """Get related asset ID."""
        return self._data.get("assetId", "")

    @property
    def has_been_seen(self) -> bool:
        """Check if issue has been viewed."""
        return self._data.get("hasBeenSeen", False)

    @property
    def is_open(self) -> bool:
        """Check if issue is open."""
        return self.status == "OPEN"

    @property
    def is_solved(self) -> bool:
        """Check if issue is solved."""
        return self.status == "SOLVED"

    @property
    def is_cancelled(self) -> bool:
        """Check if issue is cancelled."""
        return self.status == "CANCELLED"

    @property
    def is_question(self) -> bool:
        """Check if this is a question."""
        return self.type == "QUESTION"

    @property
    def display_name(self) -> str:
        """Get a human-readable display name for the issue.

        Returns the issue ID.
        """
        return self.id

    def to_dict(self) -> IssueContract:
        """Get the underlying dictionary representation."""
        return self._data
