"""Connection domain contract using TypedDict.

This module provides a TypedDict-based contract for Connection entities,
along with validation utilities and helper functions.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypedDict

from typeguard import check_type


class ConnectionContract(TypedDict, total=False):
    """TypedDict contract for Connection entities.

    This contract represents the core structure of a Connection as returned
    from the Kili API. All fields are optional to allow partial data.

    Key fields:
        id: Unique identifier for the connection
        projectId: ID of the project this connection belongs to
        lastChecked: ISO timestamp of last synchronization check
        numberOfAssets: Number of assets in this connection
        selectedFolders: List of folder paths selected for synchronization
    """

    id: str
    projectId: str
    lastChecked: Optional[str]
    numberOfAssets: int
    selectedFolders: List[str]


def validate_connection(data: Dict[str, Any]) -> ConnectionContract:
    """Validate and return a connection contract.

    Args:
        data: Dictionary to validate as a ConnectionContract

    Returns:
        The validated data as a ConnectionContract

    Raises:
        TypeError: If the data does not match the ConnectionContract structure
    """
    check_type(data, ConnectionContract)
    return data  # type: ignore[return-value]


@dataclass(frozen=True)
class ConnectionView:
    """Read-only view wrapper for ConnectionContract.

    This dataclass provides ergonomic property access to connection data
    while maintaining the underlying dictionary representation.

    Example:
        >>> connection_data = {"id": "123", "projectId": "proj_456", ...}
        >>> view = ConnectionView(connection_data)
        >>> print(view.id)
        '123'
        >>> print(view.number_of_assets)
        100
    """

    __slots__ = ("_data",)

    _data: ConnectionContract

    @property
    def id(self) -> str:
        """Get connection ID."""
        return self._data.get("id", "")

    @property
    def project_id(self) -> str:
        """Get project ID."""
        return self._data.get("projectId", "")

    @property
    def last_checked(self) -> Optional[str]:
        """Get last synchronization timestamp."""
        return self._data.get("lastChecked")

    @property
    def number_of_assets(self) -> int:
        """Get number of assets."""
        return self._data.get("numberOfAssets", 0)

    @property
    def selected_folders(self) -> List[str]:
        """Get list of selected folders."""
        return self._data.get("selectedFolders", [])

    @property
    def folder_count(self) -> int:
        """Get number of selected folders."""
        return len(self.selected_folders)

    @property
    def display_name(self) -> str:
        """Get a human-readable display name for the connection.

        Returns the connection ID.
        """
        return self.id

    def to_dict(self) -> ConnectionContract:
        """Get the underlying dictionary representation."""
        return self._data
