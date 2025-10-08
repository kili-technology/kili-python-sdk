"""Organization domain contract using TypedDict.

This module provides a TypedDict-based contract for Organization entities,
along with validation utilities and helper functions.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, TypedDict

from typeguard import check_type


class OrganizationContract(TypedDict, total=False):
    """TypedDict contract for Organization entities.

    This contract represents the core structure of an Organization as returned
    from the Kili API. All fields are optional to allow partial data.

    Key fields:
        id: Unique identifier for the organization
        name: Organization name
        address: Physical address
        city: City location
        country: Country location
        zipCode: Postal/ZIP code
        numberOfAnnotations: Total number of annotations
        numberOfLabeledAssets: Total number of labeled assets
        numberOfHours: Total hours spent on annotations
    """

    id: str
    name: str
    address: Optional[str]
    city: Optional[str]
    country: Optional[str]
    zipCode: Optional[str]
    numberOfAnnotations: int
    numberOfLabeledAssets: int
    numberOfHours: float


def validate_organization(data: Dict[str, Any]) -> OrganizationContract:
    """Validate and return an organization contract.

    Args:
        data: Dictionary to validate as an OrganizationContract

    Returns:
        The validated data as an OrganizationContract

    Raises:
        TypeError: If the data does not match the OrganizationContract structure
    """
    check_type(data, OrganizationContract)
    return data  # type: ignore[return-value]


@dataclass(frozen=True)
class OrganizationView:
    """Read-only view wrapper for OrganizationContract.

    This dataclass provides ergonomic property access to organization data
    while maintaining the underlying dictionary representation.

    Example:
        >>> org_data = {"id": "123", "name": "Acme Corp", ...}
        >>> view = OrganizationView(org_data)
        >>> print(view.id)
        '123'
        >>> print(view.display_name)
        'Acme Corp'
    """

    __slots__ = ("_data",)

    _data: OrganizationContract

    @property
    def id(self) -> str:
        """Get organization ID."""
        return self._data.get("id", "")

    @property
    def name(self) -> str:
        """Get organization name."""
        return self._data.get("name", "")

    @property
    def address(self) -> Optional[str]:
        """Get organization address."""
        return self._data.get("address")

    @property
    def city(self) -> Optional[str]:
        """Get organization city."""
        return self._data.get("city")

    @property
    def country(self) -> Optional[str]:
        """Get organization country."""
        return self._data.get("country")

    @property
    def zip_code(self) -> Optional[str]:
        """Get organization ZIP code."""
        return self._data.get("zipCode")

    @property
    def number_of_annotations(self) -> int:
        """Get total number of annotations."""
        return self._data.get("numberOfAnnotations", 0)

    @property
    def number_of_labeled_assets(self) -> int:
        """Get total number of labeled assets."""
        return self._data.get("numberOfLabeledAssets", 0)

    @property
    def number_of_hours(self) -> float:
        """Get total hours spent on annotations."""
        return self._data.get("numberOfHours", 0.0)

    @property
    def display_name(self) -> str:
        """Get a human-readable display name for the organization.

        Returns the organization name.
        """
        return self.name or self.id

    @property
    def full_address(self) -> str:
        """Get full formatted address.

        Returns:
            Formatted address string combining address, city, and country
        """
        parts = []
        if self.address:
            parts.append(self.address)
        if self.city:
            parts.append(self.city)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts) if parts else ""

    def to_dict(self) -> OrganizationContract:
        """Get the underlying dictionary representation."""
        return self._data


class OrganizationMetricsContract(TypedDict, total=False):
    """TypedDict contract for Organization Metrics.

    This contract represents organization-level metrics including
    annotation counts, hours spent, and labeled assets.

    Fields:
        numberOfAnnotations: Total number of annotations
        numberOfHours: Total hours spent on labeling
        numberOfLabeledAssets: Total number of labeled assets
    """

    numberOfAnnotations: int
    numberOfHours: float
    numberOfLabeledAssets: int


def validate_organization_metrics(data: Dict[str, Any]) -> OrganizationMetricsContract:
    """Validate and return an organization metrics contract.

    Args:
        data: Dictionary to validate as an OrganizationMetricsContract

    Returns:
        The validated data as an OrganizationMetricsContract

    Raises:
        TypeError: If the data does not match the OrganizationMetricsContract structure
    """
    check_type(data, OrganizationMetricsContract)
    return data  # type: ignore[return-value]


@dataclass(frozen=True)
class OrganizationMetricsView:
    """Read-only view wrapper for OrganizationMetricsContract.

    This dataclass provides ergonomic property access to organization metrics
    while maintaining the underlying dictionary representation.

    Example:
        >>> metrics_data = {"numberOfAnnotations": 1000, "numberOfHours": 42.5, ...}
        >>> view = OrganizationMetricsView(metrics_data)
        >>> print(view.number_of_annotations)
        1000
        >>> print(view.number_of_hours)
        42.5
    """

    __slots__ = ("_data",)

    _data: OrganizationMetricsContract

    @property
    def number_of_annotations(self) -> int:
        """Get total number of annotations."""
        return self._data.get("numberOfAnnotations", 0)

    @property
    def number_of_hours(self) -> float:
        """Get total hours spent on labeling."""
        return self._data.get("numberOfHours", 0.0)

    @property
    def number_of_labeled_assets(self) -> int:
        """Get total number of labeled assets."""
        return self._data.get("numberOfLabeledAssets", 0)

    def to_dict(self) -> OrganizationMetricsContract:
        """Get the underlying dictionary representation."""
        return self._data
