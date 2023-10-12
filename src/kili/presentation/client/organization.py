"""Organization client methods."""
from typeguard import typechecked

from kili.presentation.client.base import BaseClientMethods


class OrganizationClientMethods(BaseClientMethods):
    @typechecked
    def create_organization(
        self, name: str, address: str, zip_code: str, city: str, country: str
    ) -> Dict:
        """Create an organization.

        WARNING: This method is for internal use only.

        Each user must be linked to an organization

        Args:
            name : Name of the organization
            address : Address of the organization
            zip_code : Zip code of the organization
            city : City of the organization
            country : Country of the organization

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        organization_use_case = OrganizationUseCases(self.kili_api_gateway)
        return organization_use_case.create_organization(
            UseCaseCreateOrganizationInput(
                name=name,
                address=address,
                zip_code=zip_code,
                city=city,
                country=country,
            )
        )
