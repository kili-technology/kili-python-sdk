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


def map_create_organization_data(data: OrganizationToCreateInput) -> Dict:
    """Build the GraphQL OrganizationData variable to be sent in an operation."""
    return {
        "name": data.name,
        "address": data.address,
        "city": data.city,
        "country": data.country,
        "zipCode": data.zip_code,
    }


def map_list_organizations_where(filters: OrganizationFilters) -> Dict:
    """Build the GraphQL OrganizationWhere variable to be sent in an operation."""
    return {
        "id": filters.organization_id,
        "user": {
            "email": filters.email,
        },
    }


def map_update_organization_where(organization_id: OrganizationId) -> Dict:
    """Build the GraphQL OrganizationData variable to be sent in an operation."""
    return {"id": organization_id}


def map_update_organization_data(organization_data: OrganizationToUpdateInput) -> Dict:
    """Build the GraphQL OrganizationData variable to be sent in an operation."""
    license_str = None if not organization_data.license else json.dumps(organization_data.license)
    data = {}
    if organization_data.name is not None:
        data["name"] = organization_data.name
    if license_str is not None:
        data["license"] = license_str
    return data


def map_organization_metrics_where(filters: OrganizationMetricsFilters) -> Dict:
    """Build the GraphQL OrganizationMetricsWhere variable to be sent in an operation."""
    date_string_fmt = "%Y-%m-%dT%H:%M:%SZ"
    return {
        "organizationId": filters.id,
        "startDate": filters.start_datetime.strftime(date_string_fmt),
        "endDate": filters.end_datetime.strftime(date_string_fmt),
    }
