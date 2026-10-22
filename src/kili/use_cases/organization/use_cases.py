"""Organization use cases."""

from collections.abc import Generator

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.organization import (
    OrganizationFilters,
    OrganizationId,
    OrganizationMetricsFilters,
    OrganizationToCreateInput,
    OrganizationToUpdateInput,
    OrganizationUsageByProjectFilters,
    OrganizationUsageFilters,
)
from kili.domain.types import ListOrTuple
from kili.use_cases.base import BaseUseCases


class OrganizationUseCases(BaseUseCases):
    """Organization use cases."""

    def create_organization(self, organization_data: OrganizationToCreateInput) -> dict:
        """Create an organization."""
        return self._kili_api_gateway.create_organization(
            organization=organization_data,
        )

    def update_organization(
        self,
        organization_id: OrganizationId,
        organization_data: OrganizationToUpdateInput,
    ) -> dict:
        """Update an organization."""
        return self._kili_api_gateway.update_organization(
            organization_id=organization_id,
            organization_data=organization_data,
        )

    def list_organizations(
        self, where: OrganizationFilters, fields: ListOrTuple[str], options: QueryOptions
    ) -> Generator[dict, None, None]:
        """List organizations."""
        return self._kili_api_gateway.list_organizations(
            filters=where,
            fields=fields,
            description="List organizations",
            options=options,
        )

    def count_organizations(self, where: OrganizationFilters) -> int:
        """Count organizations."""
        return self._kili_api_gateway.count_organizations(filters=where)

    def get_organization_metrics(
        self, where: OrganizationMetricsFilters, fields: ListOrTuple[str]
    ) -> dict:
        """Get organization metrics."""
        return self._kili_api_gateway.get_organization_metrics(filters=where, fields=fields)

    def get_organization_usage(self, where: OrganizationUsageFilters) -> list[dict]:
        """Get the usage metrics of an organization."""
        return self._kili_api_gateway.get_organization_usage(filters=where)

    def list_organization_usage_by_project(
        self, where: OrganizationUsageByProjectFilters, options: QueryOptions
    ) -> Generator[dict, None, None]:
        """List the usage metrics of an organization, totalled per project."""
        return self._kili_api_gateway.list_organization_usage_by_project(
            filters=where, options=options
        )
