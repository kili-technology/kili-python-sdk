"""Integration domain contract using TypedDict.

This module provides a TypedDict-based contract for Integration entities,
along with validation utilities and helper functions.
"""

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional, TypedDict

from typeguard import check_type

# Types from domain/cloud_storage.py
DataIntegrationPlatform = Literal["AWS", "AZURE", "GCP", "S3"]
DataIntegrationStatus = Literal["CONNECTED", "CHECKING", "ERROR"]


class IntegrationContract(TypedDict, total=False):
    """TypedDict contract for Integration entities.

    This contract represents the core structure of an Integration as returned
    from the Kili API. All fields are optional to allow partial data.

    Key fields:
        id: Unique identifier for the integration
        name: Integration name
        platform: Cloud platform (AWS, AZURE, GCP, S3)
        status: Connection status (CONNECTED, CHECKING, ERROR)
        organizationId: ID of the organization owning the integration
    """

    id: str
    name: str
    platform: DataIntegrationPlatform
    status: DataIntegrationStatus
    organizationId: str


def validate_integration(data: Dict[str, Any]) -> IntegrationContract:
    """Validate and return an integration contract.

    Args:
        data: Dictionary to validate as an IntegrationContract

    Returns:
        The validated data as an IntegrationContract

    Raises:
        TypeError: If the data does not match the IntegrationContract structure
    """
    check_type(data, IntegrationContract)
    return data  # type: ignore[return-value]


@dataclass(frozen=True)
class IntegrationView:
    """Read-only view wrapper for IntegrationContract.

    This dataclass provides ergonomic property access to integration data
    while maintaining the underlying dictionary representation.

    Example:
        >>> integration_data = {"id": "123", "name": "My S3 Bucket", "platform": "AWS", ...}
        >>> view = IntegrationView(integration_data)
        >>> print(view.id)
        '123'
        >>> print(view.is_connected)
        True
    """

    __slots__ = ("_data",)

    _data: IntegrationContract

    @property
    def id(self) -> str:
        """Get integration ID."""
        return self._data.get("id", "")

    @property
    def name(self) -> str:
        """Get integration name."""
        return self._data.get("name", "")

    @property
    def platform(self) -> Optional[DataIntegrationPlatform]:
        """Get cloud platform."""
        return self._data.get("platform")

    @property
    def status(self) -> Optional[DataIntegrationStatus]:
        """Get connection status."""
        return self._data.get("status")

    @property
    def organization_id(self) -> str:
        """Get organization ID."""
        return self._data.get("organizationId", "")

    @property
    def is_connected(self) -> bool:
        """Check if integration is connected."""
        return self.status == "CONNECTED"

    @property
    def is_checking(self) -> bool:
        """Check if integration is being verified."""
        return self.status == "CHECKING"

    @property
    def has_error(self) -> bool:
        """Check if integration has an error."""
        return self.status == "ERROR"

    @property
    def is_active(self) -> bool:
        """Alias for is_connected."""
        return self.is_connected

    @property
    def display_name(self) -> str:
        """Get a human-readable display name for the integration.

        Returns the integration name.
        """
        return self.name or self.id

    def to_dict(self) -> IntegrationContract:
        """Get the underlying dictionary representation."""
        return self._data
