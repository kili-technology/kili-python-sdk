"""Organization client methods."""
from typing import Dict, Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.organization import OrganizationFilters, OrganizationId
from kili.domain.types import ListOrTuple
from kili.presentation.client.base import BaseClientMethods
from kili.use_cases.organization.use_cases import (
    OrganizationToCreateUseCaseInput,
    OrganizationUseCases,
)


class InternalOrganizationClientMethods(BaseClientMethods):
    """Organization client methods."""

    @typechecked
    def create_organization(
        self,
        name: str,
        address: str,
        zip_code: str,
        city: str,
        country: str,
        disable_tqdm: bool = False,
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
            disable_tqdm: If `True`, the progress bar will be disabled

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        organization_use_case = OrganizationUseCases(self.kili_api_gateway)
        return organization_use_case.create_organization(
            OrganizationToCreateUseCaseInput(
                name=name,
                address=address,
                zip_code=zip_code,
                city=city,
                country=country,
            ),
            disable_tqdm=disable_tqdm,
        )


class OrganizationClientMethods(BaseClientMethods):
    """Organization client methods."""

    @overload
    def organizations(
        self,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("id", "name"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]: ...

    @overload
    def organizations(
        self,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("id", "name"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]: ...

    @typechecked
    def organizations(
        self,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("id", "name"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        # pylint: disable=line-too-long
        """Get a generator or a list of organizations that match a set of criteria.

        Args:
            email: Email of a user of the organization
            organization_id: Identifier of the organization
            fields: All the fields to request among the possible fields for the organizations.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#organization) for all possible fields.
            first: Maximum number of organizations to return.
            skip: Number of skipped organizations (they are ordered by creation date)
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the organizations is returned.

        Returns:
            An iterable of organizations.

        Examples:
            >>> kili.organizations(organization_id=organization_id, fields=['users.email'])
            [{'users': [{'email': 'john@doe.com'}]}]
        """
        organization_use_cases = OrganizationUseCases(self.kili_api_gateway)
        organization_gen = organization_use_cases.list_organizations(
            OrganizationFilters(
                email=email,
                organization_id=OrganizationId(organization_id) if organization_id else None,
            ),
            fields,
            QueryOptions(disable_tqdm=disable_tqdm, first=first, skip=skip),
        )

        if as_generator:
            return organization_gen
        return list(organization_gen)

    @typechecked
    def count_organizations(
        self, email: Optional[str] = None, organization_id: Optional[str] = None
    ) -> int:
        """Count organizations that match a set of criteria.

        Args:
            email: Email of a user of the organization
            organization_id: Identifier of the organization

        Returns:
            An integer corresponding to the number of organizations that match the criteria.
        """
        where = OrganizationFilters(
            email=email,
            organization_id=OrganizationId(organization_id) if organization_id else None,
        )
        return OrganizationUseCases(self.kili_api_gateway).count_organizations(where)
