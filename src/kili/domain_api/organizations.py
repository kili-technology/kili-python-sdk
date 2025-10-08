"""Organizations domain namespace for the Kili Python SDK."""

from datetime import datetime
from typing import Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.domain_v2.organization import (
    OrganizationMetricsView,
    OrganizationView,
    validate_organization,
    validate_organization_metrics,
)
from kili.presentation.client.organization import OrganizationClientMethods


class OrganizationsNamespace(DomainNamespace):
    """Organizations domain namespace providing organization-related operations.

    This namespace provides access to all organization-related functionality
    including querying organizations, counting them, and accessing organization-level
    analytics and metrics.

    The namespace provides the following main operations:
    - list(): Query and list organizations
    - count(): Count organizations matching filters
    - metrics(): Get organization-level analytics and metrics

    Examples:
        >>> kili = Kili()
        >>> # List all organizations
        >>> organizations = kili.organizations.list()

        >>> # Get specific organization by ID
        >>> org = kili.organizations.list(organization_id="org_id", as_generator=False)

        >>> # Count organizations
        >>> count = kili.organizations.count()

        >>> # Get organization metrics
        >>> metrics = kili.organizations.metrics(
        ...     organization_id="org_id",
        ...     start_date=datetime(2024, 1, 1),
        ...     end_date=datetime(2024, 12, 31)
        ... )
    """

    def __init__(self, client, gateway):
        """Initialize the organizations namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations
        """
        super().__init__(client, gateway, "organizations")

    @overload
    def list(
        self,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("id", "name"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[OrganizationView, None, None]:
        ...

    @overload
    def list(
        self,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("id", "name"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> List[OrganizationView]:
        ...

    @typechecked
    def list(
        self,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("id", "name"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[OrganizationView]:
        """Get a generator or a list of organizations that match a set of criteria.

        Args:
            email: Email of a user of the organization
            organization_id: Identifier of the organization
            fields: All the fields to request among the possible fields for the organizations.
                See the documentation for all possible fields.
            first: Maximum number of organizations to return.
            skip: Number of skipped organizations (they are ordered by creation date)
            disable_tqdm: If True, the progress bar will be disabled
            as_generator: If True, a generator on the organizations is returned.

        Returns:
            An iterable of organizations.

        Examples:
            >>> # List all organizations
            >>> organizations = kili.organizations.list()

            >>> # Get specific organization by ID
            >>> org = kili.organizations.list(
            ...     organization_id="org_id",
            ...     as_generator=False
            ... )

            >>> # List organizations with user information
            >>> orgs = kili.organizations.list(
            ...     fields=['id', 'name', 'users.email'],
            ...     as_generator=False
            ... )

            >>> # Filter by user email
            >>> orgs = kili.organizations.list(
            ...     email="user@example.com",
            ...     as_generator=False
            ... )
        """
        # Access the legacy method directly by calling it from the mixin class
        result = OrganizationClientMethods.organizations(
            self.client,
            email=email,
            organization_id=organization_id,
            fields=fields,
            first=first,
            skip=skip,
            disable_tqdm=disable_tqdm,
            as_generator=as_generator,  # pyright: ignore[reportGeneralTypeIssues]
        )

        # Wrap results with OrganizationView
        if as_generator:
            # Create intermediate generator - iter() makes result explicitly iterable
            def _wrap_generator() -> Generator[OrganizationView, None, None]:
                result_iter = iter(result)
                for item in result_iter:
                    yield OrganizationView(validate_organization(item))

            return _wrap_generator()

        # Convert to list - list() makes result explicitly iterable
        result_list = list(result)
        return [OrganizationView(validate_organization(item)) for item in result_list]

    @typechecked
    def count(
        self,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> int:
        """Count organizations that match a set of criteria.

        Args:
            email: Email of a user of the organization
            organization_id: Identifier of the organization

        Returns:
            The number of organizations matching the criteria.

        Examples:
            >>> # Count all organizations
            >>> count = kili.organizations.count()

            >>> # Count organizations for specific user
            >>> count = kili.organizations.count(email="user@example.com")

            >>> # Check if specific organization exists
            >>> exists = kili.organizations.count(organization_id="org_id") > 0
        """
        # Access the legacy method directly by calling it from the mixin class
        return OrganizationClientMethods.count_organizations(
            self.client,
            email=email,
            organization_id=organization_id,
        )

    @typechecked
    def metrics(
        self,
        organization_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        fields: ListOrTuple[str] = (
            "numberOfAnnotations",
            "numberOfHours",
            "numberOfLabeledAssets",
        ),
    ) -> OrganizationMetricsView:
        """Get organization metrics and analytics.

        This method provides access to organization-level analytics including
        annotation counts, labeling hours, and labeled asset statistics.

        Args:
            organization_id: Identifier of the organization
            start_date: Start date of the metrics computation. If None, uses current date.
            end_date: End date of the metrics computation. If None, uses current date.
            fields: Fields to request for the organization metrics. Available fields include:
                - numberOfAnnotations: Total number of annotations
                - numberOfHours: Total hours spent on labeling
                - numberOfLabeledAssets: Total number of labeled assets

        Returns:
            A view object containing the requested metrics of the organization.

        Examples:
            >>> # Get default metrics for organization
            >>> metrics = kili.organizations.metrics(organization_id="org_id")

            >>> # Get metrics for specific date range
            >>> from datetime import datetime
            >>> metrics = kili.organizations.metrics(
            ...     organization_id="org_id",
            ...     start_date=datetime(2024, 1, 1),
            ...     end_date=datetime(2024, 12, 31)
            ... )

            >>> # Get specific metrics
            >>> metrics = kili.organizations.metrics(
            ...     organization_id="org_id",
            ...     fields=["numberOfAnnotations", "numberOfHours"]
            ... )

            >>> # Access specific metric values
            >>> annotations_count = metrics.number_of_annotations
            >>> hours_spent = metrics.number_of_hours
            >>> labeled_assets = metrics.number_of_labeled_assets
        """
        # Access the legacy method directly by calling it from the mixin class
        result = OrganizationClientMethods.organization_metrics(
            self.client,
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date,
            fields=fields,
        )
        return OrganizationMetricsView(validate_organization_metrics(result))
