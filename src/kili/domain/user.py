"""User domain."""
from dataclasses import dataclass
from typing import List, Literal, NewType, Optional

from .organization import OrganizationId

UserId = NewType("UserId", str)

HubspotSubscriptionStatus = Literal["SUBSCRIBED", "UNSUBSCRIBED"]


@dataclass
class UserFilter:
    """User filters for running a users search."""

    activated: Optional[bool]
    api_key: Optional[str]
    email: Optional[str]
    id: Optional[UserId]
    id_in: Optional[List[UserId]]
    organization_id: Optional[OrganizationId]
