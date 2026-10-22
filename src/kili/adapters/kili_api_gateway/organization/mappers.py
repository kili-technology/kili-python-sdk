"""Mappers for Organization API calls."""

import json
from datetime import datetime, timezone
from typing import Optional

from kili.domain.organization import (
    OrganizationFilters,
    OrganizationId,
    OrganizationMetricsFilters,
    OrganizationToCreateInput,
    OrganizationToUpdateInput,
    OrganizationUsageByProjectFilters,
    OrganizationUsageFilters,
)


def map_create_organization_data(data: OrganizationToCreateInput) -> dict:
    """Build the GraphQL OrganizationData variable to be sent in an operation."""
    return {
        "name": data.name,
    }


def map_list_organizations_where(filters: OrganizationFilters) -> dict:
    """Build the GraphQL OrganizationWhere variable to be sent in an operation."""
    return {
        "id": filters.organization_id,
        "user": {
            "email": filters.email,
        },
    }


def map_update_organization_where(organization_id: OrganizationId) -> dict:
    """Build the GraphQL OrganizationData variable to be sent in an operation."""
    return {"id": organization_id}


def map_update_organization_data(organization_data: OrganizationToUpdateInput) -> dict:
    """Build the GraphQL OrganizationData variable to be sent in an operation."""
    license_str = None if not organization_data.license else json.dumps(organization_data.license)
    data = {}
    if organization_data.name is not None:
        data["name"] = organization_data.name
    if license_str is not None:
        data["license"] = license_str
    return data


def map_organization_metrics_where(filters: OrganizationMetricsFilters) -> dict:
    """Build the GraphQL OrganizationMetricsWhere variable to be sent in an operation."""
    date_string_fmt = "%Y-%m-%dT%H:%M:%SZ"
    return {
        "organizationId": filters.id,
        "startDate": filters.start_datetime.strftime(date_string_fmt),
        "endDate": filters.end_datetime.strftime(date_string_fmt),
    }


def _to_utc_iso(date: Optional[datetime]) -> Optional[str]:
    """Format a date in UTC ISO 8601, reading a naive datetime as UTC."""
    if date is None:
        return None
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)
    return date.astimezone(timezone.utc).isoformat()


def map_organization_usage_where(filters: OrganizationUsageFilters) -> dict:
    """Build the GraphQL OrganizationMetricsAnalyticsWhere variable to be sent in an operation."""
    where = {
        "metrics": list(filters.metrics),
        "organizationId": filters.organization_id,
        "projectId": filters.project_id,
        "startDate": _to_utc_iso(filters.start_datetime),
        "endDate": _to_utc_iso(filters.end_datetime),
        "granularity": filters.granularity,
    }
    return {key: value for key, value in where.items() if value is not None}


def map_organization_usage_by_project_where(filters: OrganizationUsageByProjectFilters) -> dict:
    """Build the GraphQL OrganizationProjectMetricsWhere variable to be sent in an operation."""
    where = {
        "metrics": list(filters.metrics),
        "organizationId": filters.organization_id,
        "startDate": _to_utc_iso(filters.start_datetime),
        "endDate": _to_utc_iso(filters.end_datetime),
        "searchQuery": filters.search_query,
    }
    return {key: value for key, value in where.items() if value is not None}
