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

    activated: Optional[bool] = None
    api_key: Optional[str] = None
    # auth0_id: Optional[str] = None  # refused by the backend: only used for service account  # noqa: ERA001  # pylint: disable=line-too-long
    email: Optional[str] = None
    firstname: Optional[str] = None
    has_completed_labeling_tour: Optional[bool] = None
    hubspot_subscription_status: Optional[HubspotSubscriptionStatus] = None
    lastname: Optional[str] = None
    organization: Optional[str] = None
    organization_id: Optional[OrganizationId] = None
    organization_role: Optional[OrganizationRole] = None
