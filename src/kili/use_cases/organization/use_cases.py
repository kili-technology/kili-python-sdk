"""Organization use cases."""
from dataclasses import dataclass
from typing import Dict, Generator, Optional

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.organization.types import (
    KiliAPIGateWayCreateOrganizationInput,
)
from kili.domain.organization import (
    Organization,
    OrganizationFilters,
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


class OrganizationUseCases(BaseUseCases):
    """Organization use cases."""

    def create_organization(
        self, organization: OrganizationToCreateUseCaseInput, disable_tqdm: bool
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
