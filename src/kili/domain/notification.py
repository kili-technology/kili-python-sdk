"""Notification domain."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, NewType, Optional

if TYPE_CHECKING:
    from .user import UserFilter

NotificationId = NewType("NotificationId", str)


@dataclass
class NotificationFilter:
    """Notification filter."""

    has_been_seen: Optional[bool]
    id: Optional[NotificationId]
    user: Optional["UserFilter"]
