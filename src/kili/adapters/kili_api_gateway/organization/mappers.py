"""Mappers for Organization API calls."""
from typing import Dict

from kili.adapters.kili_api_gateway.organization.types import (
    KiliAPIGateWayCreateOrganizationInput,
)
from kili.domain.organization import OrganizationFilters


def map_organization_data(data: KiliAPIGateWayCreateOrganizationInput) -> Dict:
    """Build the GraphQL OrganizationData variable to be sent in an operation."""
    return {
        "data": {
            "name": data.name,
            "address": data.address,
            "city": data.city,
            "country": data.country,
            "zipCode": data.zip_code,
        }
    }


def map_organization_where(filters: OrganizationFilters) -> Dict:
    """Build the GraphQL OrganizationWhere variable to be sent in an operation."""
    return {
        "id": filters.organization_id,
        "user": {
            "email": filters.email,
        },
    }
