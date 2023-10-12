"""Mappers for Organization API calls."""
from typing import Dict

from kili.adapters.kili_api_gateway.organization.types import (
    KiliAPIGateWayCreateOrganizationInput,
)


def map_organization_data(data: KiliAPIGateWayCreateOrganizationInput) -> Dict:
    """Build the GraphQL OrganizationData variable to be sent in an operation."""
    return {
        "name": data.name,
        "address": data.address,
        "city": data.city,
        "country": data.country,
        "zipCode": data.zip_code,
    }
