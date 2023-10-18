"""Organization use cases."""
from dataclasses import dataclass
from typing import Dict, Generator, Optional

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.organization.types import (
    KiliAPIGateWayCreateOrganizationInput,
    KiliAPIGateWayUpdateOrganizationInput,
)
from kili.domain.organization import (
    Organization,
    OrganizationFilters,
    OrganizationId,
    OrganizationMetricsFilters,
)
from kili.domain.types import ListOrTuple
from kili.use_cases.base import BaseUseCases


@dataclass
class OrganizationToCreateUseCaseInput:
    """Organization to create use case input."""

    name: str
    address: str
    city: str
    country: str
    zip_code: str


@dataclass
class OrganizationToUpdateUseCaseInput:
    """Organization to update use case input."""

    name: Optional[str]
    license: Optional[Dict]  # noqa: A003


class OrganizationUseCases(BaseUseCases):
    """Organization use cases."""

    def create_organization(
        self, organization: OrganizationToCreateUseCaseInput, disable_tqdm: Optional[bool]
    ) -> Organization:
        """Create an organization."""
        return self._kili_api_gateway.create_organization(
            KiliAPIGateWayCreateOrganizationInput(
                name=organization.name,
                address=organization.address,
                city=organization.city,
                country=organization.country,
                zip_code=organization.zip_code,
            ),
            description="Create organization",
            disable_tqdm=disable_tqdm,
        )

    def update_organization(
        self,
        organization_id: OrganizationId,
        organization: OrganizationToUpdateUseCaseInput,
        disable_tqdm: Optional[bool],
    ) -> Organization:
        """Update an organization."""
        return self._kili_api_gateway.update_organization(
            organization_id=organization_id,
            organization_data=KiliAPIGateWayUpdateOrganizationInput(
                name=organization.name, license=organization.license
            ),
            description="Update organization",
            disable_tqdm=disable_tqdm,
        )

    def list_organizations(
        self, where: OrganizationFilters, fields: ListOrTuple[str], options: QueryOptions
    ) -> Generator[Dict, None, None]:
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
        self, where: OrganizationMetricsFilters, disable_tqdm: Optional[bool]
    ) -> Dict:
        """Get organization metrics."""
        return self._kili_api_gateway.get_organization_metrics(
            filters=where, description="Retrieve organization metrics", disable_tqdm=disable_tqdm
        )
