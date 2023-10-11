"""Types for the user-related Kili API gateway functions."""
from dataclasses import dataclass
from typing import Optional

from kili.core.enums import OrganizationRole
from kili.domain.organization import OrganizationId
from kili.domain.user import HubspotSubscriptionStatus


@dataclass
class CreateUserDataKiliGatewayInput:
    """Input type for creating a user in Kili Gateway."""

    email: str
    firstname: Optional[str]
    lastname: Optional[str]
    password: Optional[str]
    organization_role: OrganizationRole


@dataclass
class UserDataKiliGatewayInput:
    """Input type for updating a user in Kili Gateway."""

    activated: Optional[bool]
    api_key: Optional[str]
    auth0_id: Optional[str]
    email: Optional[str]
    firstname: Optional[str]
    has_completed_labeling_tour: Optional[bool]
    hubspot_subscription_status: Optional[HubspotSubscriptionStatus]
    lastname: Optional[str]
    organization: Optional[str]
    organization_id: Optional[OrganizationId]
    organization_role: Optional[OrganizationRole]
