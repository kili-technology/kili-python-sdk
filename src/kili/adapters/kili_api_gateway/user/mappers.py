"""GraphQL payload data mappers for user operations."""

from typing import Dict

from kili.domain.user import UserFilter

from .types import CreateUserDataKiliGatewayInput, UserDataKiliGatewayInput


def user_where_mapper(filters: UserFilter) -> Dict:
    """Build the GraphQL UserWhere variable to be sent in an operation."""
    return {
        "activated": filters.activated,
        "apiKey": filters.api_key,
        "email": filters.email,
        "id": filters.id,
        "idIn": filters.id_in,
        "organization": {"id": filters.organization_id},
    }


def create_user_data_mapper(data: CreateUserDataKiliGatewayInput) -> Dict:
    """Build the CreateUserDataKiliGatewayInput data variable to be sent in an operation."""
    return {
        "email": data.email.lower(),
        "firstname": data.firstname,
        "lastname": data.lastname,
        "password": data.password,
        "organizationRole": data.organization_role,
    }


def update_user_data_mapper(data: UserDataKiliGatewayInput) -> Dict:
    """Build the UserDataKiliGatewayInput data variable to be sent in an operation."""
    return {
        "activated": data.activated,
        "apiKey": data.api_key,
        # "auth0Id": data.auth0_id,  # refused by the backend: only used for service account  # noqa: ERA001  # pylint: disable=line-too-long
        "email": data.email,
        "firstname": data.firstname,
        "hasCompletedLabelingTour": data.has_completed_labeling_tour,
        "hubspotSubscriptionStatus": data.hubspot_subscription_status,
        "lastname": data.lastname,
        "organization": data.organization,
        "organizationId": data.organization_id,
        "organizationRole": data.organization_role,
    }
