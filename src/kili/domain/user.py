"""User domain."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, NewType, Optional

if TYPE_CHECKING:
    from .organization import OrganizationId

UserId = NewType("UserId", str)

HubspotSubscriptionStatus = Literal["SUBSCRIBED", "UNSUBSCRIBED"]


@dataclass
class UserFilter:
    """User filters for running a users search."""

    id: Optional[UserId]
    activated: Optional[bool] = None
    email: Optional[str] = None
    id_in: Optional[list[UserId]] = None
    organization_id: Optional["OrganizationId"] = None
