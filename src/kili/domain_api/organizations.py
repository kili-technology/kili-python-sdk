"""Organizations domain namespace for the Kili Python SDK."""

from datetime import datetime
from typing import Dict, Generator, List, Optional

from typeguard import typechecked
from typing_extensions import deprecated

from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.domain_api.namespace_utils import get_available_methods


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

    @deprecated(
        "'organizations' is a namespace, not a callable method. "
        "Use kili.organizations.list() or other available methods instead."
    )
    def __call__(self, *args, **kwargs):
        """Raise a helpful error when namespace is called like a method.

        This provides guidance to users migrating from the legacy API
        where organizations were accessed via kili.organizations(...) to the new domain API
        where they use kili.organizations.list(...) or other methods.
        """
        available_methods = get_available_methods(self)
        methods_str = ", ".join(f"kili.{self._domain_name}.{m}()" for m in available_methods)
        raise TypeError(
            f"'{self._domain_name}' is a namespace, not a callable method. "
            f"The legacy API 'kili.{self._domain_name}(...)' has been replaced with the domain API.\n"
            f"Available methods: {methods_str}\n"
            f"Example: kili.{self._domain_name}.list(...)"
        )

    @typechecked
    def list(
        self,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("id", "name"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
    ) -> List[Dict]:
        """Get a list of organizations that match a set of criteria.

        Args:
            email: Email of a user of the organization
            organization_id: Identifier of the organization
            fields: All the fields to request among the possible fields for the organizations.
                See the documentation for all possible fields.
            first: Maximum number of organizations to return.
            skip: Number of skipped organizations (they are ordered by creation date)
            disable_tqdm: If True, the progress bar will be disabled

        Returns:
            A list of organizations.

        Examples:
            >>> # List all organizations
            >>> organizations = kili.organizations.list()

            >>> # Get specific organization by ID
            >>> org = kili.organizations.list(organization_id="org_id")

            >>> # List organizations with user information
            >>> orgs = kili.organizations.list(fields=['id', 'name', 'users.email'])

            >>> # Filter by user email
            >>> orgs = kili.organizations.list(email="user@example.com")
        """
        return self._client.organizations(
            email=email,
            organization_id=organization_id,
            fields=fields,
            first=first,
            skip=skip,
            disable_tqdm=disable_tqdm,
            as_generator=False,
        )

    @typechecked
    def list_as_generator(
        self,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("id", "name"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
    ) -> Generator[Dict, None, None]:
        """Get a generator of organizations that match a set of criteria.

        Args:
            email: Email of a user of the organization
            organization_id: Identifier of the organization
            fields: All the fields to request among the possible fields for the organizations.
                See the documentation for all possible fields.
            first: Maximum number of organizations to return.
            skip: Number of skipped organizations (they are ordered by creation date)
            disable_tqdm: If True, the progress bar will be disabled

        Returns:
            A generator yielding organizations.

        Examples:
            >>> # Get organizations as generator
            >>> for org in kili.organizations.list_as_generator():
            ...     print(org["name"])
        """
        return self._client.organizations(
            email=email,
            organization_id=organization_id,
            fields=fields,
            first=first,
            skip=skip,
            disable_tqdm=disable_tqdm,
            as_generator=True,
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
    ) -> Dict:
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
            A dictionary containing the requested metrics of the organization.

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
            >>> annotations_count = metrics["numberOfAnnotations"]
            >>> hours_spent = metrics["numberOfHours"]
        """
        return self._client.organization_metrics(
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date,
            fields=fields,
        )
