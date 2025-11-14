"""Kili Python SDK client."""

import logging
import warnings
from functools import cached_property
from typing import TYPE_CHECKING, Dict, Optional, Union

from kili.client import Kili as KiliLegacy
from kili.core.graphql.graphql_client import GraphQLClientName

if TYPE_CHECKING:
    from kili.domain_api import (
        AssetsNamespace,
        ExportNamespace,
        IssuesNamespace,
        LabelsNamespace,
        OrganizationsNamespace,
        ProjectsNamespace,
        QuestionsNamespace,
        StoragesNamespace,
        TagsNamespace,
        UsersNamespace,
    )

warnings.filterwarnings("default", module="kili", category=DeprecationWarning)


class FilterPoolFullWarning(logging.Filter):
    """Filter out the specific urllib3 warning related to the connection pool."""

    def filter(self, record) -> bool:
        """urllib3.connectionpool:Connection pool is full, discarding connection: ..."""
        return "Connection pool is full, discarding connection" not in record.getMessage()


logging.getLogger("urllib3.connectionpool").addFilter(FilterPoolFullWarning())


class Kili:
    """Kili Client (domain mode)."""

    legacy_client: KiliLegacy

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        verify: Optional[Union[bool, str]] = None,
        graphql_client_params: Optional[Dict[str, object]] = None,
    ) -> None:
        """Initialize Kili client (domain mode).

        This client provides access to domain-based namespaces.
        For the legacy API with methods, use `from kili.client import Kili` instead.

        Args:
            api_key: User API key generated
                from https://cloud.kili-technology.com/label/my-account/api-key.
                Default to `KILI_API_KEY` environment variable.
                If not passed, requires the `KILI_API_KEY` environment variable to be set.
            api_endpoint: Recipient of the HTTP operation.
                Default to `KILI_API_ENDPOINT` environment variable.
                If not passed, default to Kili SaaS:
                'https://cloud.kili-technology.com/api/label/v2/graphql'
            verify: similar to `requests`' verify.
                Either a boolean, in which case it controls whether we verify
                the server's TLS certificate, or a string, in which case it must be a path
                to a CA bundle to use. Defaults to ``True``. When set to
                ``False``, requests will accept any TLS certificate presented by
                the server, and will ignore hostname mismatches and/or expired
                certificates, which will make your application vulnerable to
                man-in-the-middle (MitM) attacks. Setting verify to ``False``
                may be useful during local development or testing.
            graphql_client_params: Parameters to pass to the graphQL client.

        Returns:
            Instance of the Kili client.

        Examples:
            ```python
            from kili.client_domain import Kili

            # Domain API with namespaces
            kili = Kili()
            kili.assets  # domain namespace (clean name)
            kili.projects.list()  # domain methods
            ```
        """
        warnings.warn(
            "Client domain api is still a work in progress. Method names and return type will evolve.",
            stacklevel=1,
        )
        self.legacy_client = KiliLegacy(
            api_key,
            api_endpoint,
            verify,
            GraphQLClientName.SDK_DOMAIN,
            graphql_client_params,
        )

    # Domain API Namespaces - Lazy loaded properties
    @cached_property
    def assets(self) -> "AssetsNamespace":
        """Get the assets domain namespace.

        Returns:
            AssetsNamespace: Assets domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            assets = kili.assets
            ```
        """
        from kili.domain_api import AssetsNamespace  # pylint: disable=import-outside-toplevel

        return AssetsNamespace(self.legacy_client, self.legacy_client.kili_api_gateway)

    @cached_property
    def labels(self) -> "LabelsNamespace":
        """Get the labels domain namespace.

        Returns:
            LabelsNamespace: Labels domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            labels = kili.labels
            ```
        """
        from kili.domain_api import LabelsNamespace  # pylint: disable=import-outside-toplevel

        return LabelsNamespace(self.legacy_client, self.legacy_client.kili_api_gateway)

    @cached_property
    def projects(self) -> "ProjectsNamespace":
        """Get the projects domain namespace.

        Returns:
            ProjectsNamespace: Projects domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            projects = kili.projects
            ```
        """
        from kili.domain_api import ProjectsNamespace  # pylint: disable=import-outside-toplevel

        return ProjectsNamespace(self.legacy_client, self.legacy_client.kili_api_gateway)

    @cached_property
    def users(self) -> "UsersNamespace":
        """Get the users domain namespace.

        Returns:
            UsersNamespace: Users domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            users = kili.users
            ```
        """
        from kili.domain_api import UsersNamespace  # pylint: disable=import-outside-toplevel

        return UsersNamespace(self.legacy_client, self.legacy_client.kili_api_gateway)

    @cached_property
    def organizations(self) -> "OrganizationsNamespace":
        """Get the organizations domain namespace.

        Returns:
            OrganizationsNamespace: Organizations domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            organizations = kili.organizations
            ```
        """
        from kili.domain_api import (  # pylint: disable=import-outside-toplevel
            OrganizationsNamespace,
        )

        return OrganizationsNamespace(self.legacy_client, self.legacy_client.kili_api_gateway)

    @cached_property
    def issues(self) -> "IssuesNamespace":
        """Get the issues domain namespace.

        Returns:
            IssuesNamespace: Issues domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            issues = kili.issues
            ```
        """
        from kili.domain_api import IssuesNamespace  # pylint: disable=import-outside-toplevel

        return IssuesNamespace(self.legacy_client, self.legacy_client.kili_api_gateway)

    @cached_property
    def questions(self) -> "QuestionsNamespace":
        """Get the questions domain namespace.

        Returns:
            QuestionsNamespace: Questions domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            questions = kili.questions
            ```
        """
        from kili.domain_api import QuestionsNamespace  # pylint: disable=import-outside-toplevel

        return QuestionsNamespace(self.legacy_client, self.legacy_client.kili_api_gateway)

    @cached_property
    def tags(self) -> "TagsNamespace":
        """Get the tags domain namespace.

        Returns:
            TagsNamespace: Tags domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            tags = kili.tags
            ```
        """
        from kili.domain_api import TagsNamespace  # pylint: disable=import-outside-toplevel

        return TagsNamespace(self.legacy_client, self.legacy_client.kili_api_gateway)

    @cached_property
    def storages(self) -> "StoragesNamespace":
        """Get the storages domain namespace.

        Returns:
            StoragesNamespace: Storages domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            storages = kili.storages
            # Access nested namespaces
            integrations = kili.storages.integrations
            connections = kili.storages.connections
            ```
        """
        from kili.domain_api import StoragesNamespace  # pylint: disable=import-outside-toplevel

        return StoragesNamespace(self.legacy_client, self.legacy_client.kili_api_gateway)

    @cached_property
    def exports(self) -> "ExportNamespace":
        """Get the exports domain namespace.

        Returns:
            ExportNamespace: Exports domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            exports = kili.exports
            ```
        """
        from kili.domain_api import ExportNamespace  # pylint: disable=import-outside-toplevel

        return ExportNamespace(self.legacy_client, self.legacy_client.kili_api_gateway)
