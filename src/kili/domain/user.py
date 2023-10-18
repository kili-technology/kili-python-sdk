"""User domain."""

from dataclasses import dataclass
from typing import List, Literal, NewType, Optional

from .organization import OrganizationId

UserId = NewType("UserId", str)

HubspotSubscriptionStatus = Literal["SUBSCRIBED", "UNSUBSCRIBED"]


@dataclass
class UserFilter:
    """User filters for running a users search."""

    id: Optional[UserId]  # noqa: A003
    activated: Optional[bool] = None
    api_key: Optional[str] = None
    email: Optional[str] = None
    id_in: Optional[List[UserId]] = None
    organization_id: Optional[OrganizationId] = None
