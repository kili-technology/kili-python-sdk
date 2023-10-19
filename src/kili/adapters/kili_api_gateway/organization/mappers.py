"""Mappers for Organization API calls."""

import json
from typing import Dict

from kili.domain.organization import (
    OrganizationFilters,
    OrganizationId,
    OrganizationMetricsFilters,
    OrganizationToCreateInput,
    OrganizationToUpdateInput,
)


def map_organization_data(data: OrganizationToCreateInput) -> Dict:
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


def map_organization_metrics_where(filters: OrganizationMetricsFilters) -> Dict:
    """Build the GraphQL OrganizationMetricsWhere variable to be sent in an operation."""
    date_string_fmt = "%Y-%m-%dT%H:%M:%SZ"
    return {
        "organizationId": filters.id,
        "startDate": filters.start_datetime.strftime(date_string_fmt),
        "endDate": filters.end_datetime.strftime(date_string_fmt),
    }


def map_organization_update_data(
    organization_id: OrganizationId, organization_data: OrganizationToUpdateInput
) -> Dict:
    """Build the GraphQL OrganizationData variable to be sent in an operation."""
    license_str = None if not organization_data.license else json.dumps(organization_data.license)
    variables = {"where": {"id": str(organization_id)}}
    variables["data"] = {}
    if organization_data.name is not None:
        variables["data"]["name"] = organization_data.name
    if license_str is not None:
        variables["data"]["license"] = license_str

    return variables
