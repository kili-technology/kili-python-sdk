"""Notification domain."""

from dataclasses import dataclass
from typing import NewType, Optional

NotificationId = NewType("NotificationId", str)


@dataclass
class NotificationFilter:
    """Notification filter."""

    id: Optional[NotificationId]
