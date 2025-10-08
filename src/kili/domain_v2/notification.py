"""Notification domain contract using TypedDict.

This module provides a TypedDict-based contract for Notification entities,
along with validation utilities and helper functions.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, TypedDict

from typeguard import check_type


class NotificationContract(TypedDict, total=False):
    """TypedDict contract for Notification entities.

    This contract represents the core structure of a Notification as returned
    from the Kili API. All fields are optional to allow partial data.

    Key fields:
        id: Unique identifier for the notification
        createdAt: ISO timestamp of creation
        message: Notification message content
        status: Notification status/priority
        userID: ID of the user receiving the notification
        url: Optional URL for the notification action
        hasBeenSeen: Whether the notification has been viewed
    """

    id: str
    createdAt: str
    message: str
    status: str
    userID: str
    url: Optional[str]
    hasBeenSeen: bool


def validate_notification(data: Dict[str, Any]) -> NotificationContract:
    """Validate and return a notification contract.

    Args:
        data: Dictionary to validate as a NotificationContract

    Returns:
        The validated data as a NotificationContract

    Raises:
        TypeError: If the data does not match the NotificationContract structure
    """
    check_type(data, NotificationContract)
    return data  # type: ignore[return-value]


@dataclass(frozen=True)
class NotificationView:
    """Read-only view wrapper for NotificationContract.

    This dataclass provides ergonomic property access to notification data
    while maintaining the underlying dictionary representation.

    Example:
        >>> notification_data = {"id": "123", "message": "Task completed", ...}
        >>> view = NotificationView(notification_data)
        >>> print(view.id)
        '123'
        >>> print(view.has_been_seen)
        False
    """

    __slots__ = ("_data",)

    _data: NotificationContract

    @property
    def id(self) -> str:
        """Get notification ID."""
        return self._data.get("id", "")

    @property
    def created_at(self) -> Optional[str]:
        """Get creation timestamp."""
        return self._data.get("createdAt")

    @property
    def message(self) -> str:
        """Get notification message."""
        return self._data.get("message", "")

    @property
    def status(self) -> str:
        """Get notification status."""
        return self._data.get("status", "")

    @property
    def user_id(self) -> str:
        """Get user ID."""
        return self._data.get("userID", "")

    @property
    def url(self) -> Optional[str]:
        """Get notification URL."""
        return self._data.get("url")

    @property
    def has_been_seen(self) -> bool:
        """Check if notification has been seen."""
        return self._data.get("hasBeenSeen", False)

    @property
    def is_unread(self) -> bool:
        """Check if notification is unread."""
        return not self.has_been_seen

    @property
    def display_name(self) -> str:
        """Get a human-readable display name for the notification.

        Returns a truncated version of the message.
        """
        if len(self.message) > 50:
            return self.message[:47] + "..."
        return self.message or self.id

    def to_dict(self) -> NotificationContract:
        """Get the underlying dictionary representation."""
        return self._data
