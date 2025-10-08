"""User domain contract using TypedDict.

This module provides a TypedDict-based contract for User entities,
along with validation utilities and helper functions.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

from typeguard import check_type

# Types from domain/user.py
HubspotSubscriptionStatus = Literal["SUBSCRIBED", "UNSUBSCRIBED"]


class OrganizationRoleContract(TypedDict, total=False):
    """Organization role information."""

    id: str
    role: Literal["ADMIN", "USER", "REVIEWER"]


class UserContract(TypedDict, total=False):
    """TypedDict contract for User entities.

    This contract represents the core structure of a User as returned
    from the Kili API. All fields are optional to allow partial data.

    Key fields:
        id: Unique identifier for the user
        email: User email address
        name: User display name
        firstname: User first name
        lastname: User last name
        activated: Whether the user account is activated
        organizationRole: User role in organization
        createdAt: ISO timestamp of account creation
    """

    id: str
    email: str
    name: str
    firstname: str
    lastname: str
    activated: bool
    createdAt: str
    updatedAt: str
    organizationId: str
    organizationRole: Union[str, OrganizationRoleContract]  # API can return string or dict
    apiKey: str
    phone: Optional[str]
    hubspotSubscriptionStatus: HubspotSubscriptionStatus
    lastSeenAt: Optional[str]


def validate_user(data: Dict[str, Any]) -> UserContract:
    """Validate and return a user contract.

    Args:
        data: Dictionary to validate as a UserContract

    Returns:
        The validated data as a UserContract

    Raises:
        TypeError: If the data does not match the UserContract structure
    """
    check_type(data, UserContract)
    return data  # type: ignore[return-value]


@dataclass(frozen=True)
class UserView:
    """Read-only view wrapper for UserContract.

    This dataclass provides ergonomic property access to user data
    while maintaining the underlying dictionary representation.

    Example:
        >>> user_data = {"id": "101", "email": "user@example.com", ...}
        >>> view = UserView(user_data)
        >>> print(view.id)
        '101'
        >>> print(view.display_name)
        'user@example.com'
    """

    __slots__ = ("_data",)

    _data: UserContract

    @property
    def id(self) -> str:
        """Get user ID."""
        return self._data.get("id", "")

    @property
    def email(self) -> str:
        """Get user email."""
        return self._data.get("email", "")

    @property
    def name(self) -> str:
        """Get user name."""
        return self._data.get("name", "")

    @property
    def firstname(self) -> str:
        """Get user first name."""
        return self._data.get("firstname", "")

    @property
    def lastname(self) -> str:
        """Get user last name."""
        return self._data.get("lastname", "")

    @property
    def activated(self) -> bool:
        """Check if user account is activated."""
        return self._data.get("activated", False)

    @property
    def created_at(self) -> Optional[str]:
        """Get account creation timestamp."""
        return self._data.get("createdAt")

    @property
    def updated_at(self) -> Optional[str]:
        """Get account update timestamp."""
        return self._data.get("updatedAt")

    @property
    def organization_id(self) -> str:
        """Get organization ID."""
        return self._data.get("organizationId", "")

    @property
    def organization_role(self) -> Optional[Union[str, OrganizationRoleContract]]:
        """Get organization role (can be string or dict depending on API response)."""
        return self._data.get("organizationRole")

    @property
    def phone(self) -> Optional[str]:
        """Get phone number."""
        return self._data.get("phone")

    @property
    def last_seen_at(self) -> Optional[str]:
        """Get last seen timestamp."""
        return self._data.get("lastSeenAt")

    @property
    def display_name(self) -> str:
        """Get a human-readable display name for the user.

        Returns the name if available, otherwise the email.
        """
        return self.name or self.email or self.id

    @property
    def full_name(self) -> str:
        """Get full name from firstname and lastname.

        Returns:
            Full name or falls back to name/email if not available
        """
        if self.firstname or self.lastname:
            return f"{self.firstname} {self.lastname}".strip()
        return self.name or self.email

    @property
    def is_admin(self) -> bool:
        """Check if user is an organization admin."""
        role = self.organization_role
        if not role:
            return False
        # Handle both string and dict formats
        # API can return either "ADMIN" (string) or {"role": "ADMIN", ...} (dict)
        if isinstance(role, str):
            return role == "ADMIN"
        if isinstance(role, dict):
            return role.get("role") == "ADMIN"
        return False

    def to_dict(self) -> UserContract:
        """Get the underlying dictionary representation."""
        return self._data


def sort_users_by_email(users: List[UserContract], reverse: bool = False) -> List[UserContract]:
    """Sort users by email address.

    Args:
        users: List of user contracts to sort
        reverse: If True, sort in descending order

    Returns:
        Sorted list of users
    """
    return sorted(
        users,
        key=lambda user: user.get("email", ""),
        reverse=reverse,
    )


def filter_users_by_activated(
    users: List[UserContract], activated: bool = True
) -> List[UserContract]:
    """Filter users by activation status.

    Args:
        users: List of user contracts to filter
        activated: If True, return only activated users; if False, only deactivated

    Returns:
        Filtered list of users
    """
    return [user for user in users if user.get("activated") == activated]
