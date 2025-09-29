"""Kili Python SDK client."""

import getpass
import logging
import os
import sys
import warnings
from functools import cached_property
from typing import Dict, Optional, Union

from kili.adapters.authentification import is_api_key_valid
from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.core.graphql.graphql_client import GraphQLClient, GraphQLClientName
from kili.domain_api import (
    AssetsNamespace,
    CloudStorageNamespace,
    ConnectionsNamespace,
    IntegrationsNamespace,
    IssuesNamespace,
    LabelsNamespace,
    NotificationsNamespace,
    OrganizationsNamespace,
    ProjectsNamespace,
    TagsNamespace,
    UsersNamespace,
)
from kili.entrypoints.mutations.asset import MutationsAsset
from kili.entrypoints.mutations.issue import MutationsIssue
from kili.entrypoints.mutations.notification import MutationsNotification
from kili.entrypoints.mutations.plugins import MutationsPlugins
from kili.entrypoints.mutations.project import MutationsProject
from kili.entrypoints.mutations.project_version import MutationsProjectVersion
from kili.entrypoints.queries.plugins import QueriesPlugins
from kili.entrypoints.queries.project_user import QueriesProjectUser
from kili.entrypoints.queries.project_version import QueriesProjectVersion
from kili.entrypoints.subscriptions.label import SubscriptionsLabel
from kili.event.presentation.client.event import EventClientMethods
from kili.exceptions import AuthenticationFailed
from kili.llm.presentation.client.llm import LlmClientMethods
from kili.presentation.client.asset import AssetClientMethods
from kili.presentation.client.cloud_storage import CloudStorageClientMethods
from kili.presentation.client.internal import InternalClientMethods
from kili.presentation.client.issue import IssueClientMethods
from kili.presentation.client.label import LabelClientMethods
from kili.presentation.client.notification import NotificationClientMethods
from kili.presentation.client.organization import OrganizationClientMethods
from kili.presentation.client.project import ProjectClientMethods
from kili.presentation.client.project_workflow import ProjectWorkflowClientMethods
from kili.presentation.client.tag import TagClientMethods
from kili.presentation.client.user import UserClientMethods
from kili.use_cases.api_key import ApiKeyUseCases

warnings.filterwarnings("default", module="kili", category=DeprecationWarning)


class FilterPoolFullWarning(logging.Filter):
    """Filter out the specific urllib3 warning related to the connection pool."""

    def filter(self, record) -> bool:
        """urllib3.connectionpool:Connection pool is full, discarding connection: ..."""
        return "Connection pool is full, discarding connection" not in record.getMessage()


logging.getLogger("urllib3.connectionpool").addFilter(FilterPoolFullWarning())


class Kili(  # pylint: disable=too-many-ancestors,too-many-instance-attributes
    MutationsAsset,
    MutationsIssue,
    MutationsNotification,
    MutationsPlugins,
    MutationsProject,
    MutationsProjectVersion,
    QueriesPlugins,
    QueriesProjectUser,
    QueriesProjectVersion,
    SubscriptionsLabel,
    AssetClientMethods,
    CloudStorageClientMethods,
    IssueClientMethods,
    LabelClientMethods,
    NotificationClientMethods,
    OrganizationClientMethods,
    ProjectClientMethods,
    ProjectWorkflowClientMethods,
    TagClientMethods,
    UserClientMethods,
):
    """Kili Client."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        verify: Optional[Union[bool, str]] = None,
        client_name: GraphQLClientName = GraphQLClientName.SDK,
        graphql_client_params: Optional[Dict[str, object]] = None,
        legacy: bool = True,
    ) -> None:
        """Initialize Kili client.

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
            client_name: For internal use only.
                Define the name of the graphQL client whith which graphQL calls will be sent.
            graphql_client_params: Parameters to pass to the graphQL client.
            legacy: Controls namespace naming and legacy method availability.
                When True (default), legacy methods are available and domain namespaces
                use the '_ns' suffix (e.g., kili.assets_ns).
                When False, legacy methods are not available and domain namespaces
                use clean names (e.g., kili.assets).

        Returns:
            Instance of the Kili client.

        Examples:
            ```python
            from kili.client import Kili

            # Legacy mode (default)
            kili = Kili()
            kili.assets()  # legacy method
            kili.assets_ns  # domain namespace

            # Modern mode
            kili = Kili(legacy=False)
            kili.assets  # domain namespace (clean name)
            # kili.assets() not available
            ```
        """
        api_key = api_key or os.getenv("KILI_API_KEY")

        if not api_key and sys.stdin.isatty():
            api_key = getpass.getpass(
                "No `KILI_API_KEY` environment variable found.\nPlease enter your API key: "
            )

        if api_endpoint is None:
            api_endpoint = os.getenv(
                "KILI_API_ENDPOINT",
                "https://cloud.kili-technology.com/api/label/v2/graphql",
            )

        if not api_key:
            raise AuthenticationFailed(api_key, api_endpoint)

        if verify is None:
            verify = os.getenv(
                "KILI_VERIFY",
                "True",
            ).lower() in ("true", "1", "yes")

        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.verify = verify
        self.client_name = client_name
        self._legacy_mode = legacy
        self.http_client = HttpClient(kili_endpoint=api_endpoint, verify=verify, api_key=api_key)
        skip_checks = os.getenv("KILI_SDK_SKIP_CHECKS") is not None
        if not skip_checks and not is_api_key_valid(
            self.http_client, api_key, api_endpoint, client_name
        ):
            raise AuthenticationFailed(
                api_key=self.api_key,
                api_endpoint=self.api_endpoint,
                error_msg="Api key does not seem to be valid.",
            )

        self.graphql_client = GraphQLClient(
            endpoint=api_endpoint,
            api_key=api_key,
            client_name=client_name,
            verify=self.verify,
            http_client=self.http_client,
            **(graphql_client_params or {}),  # pyright: ignore[reportGeneralTypeIssues]
        )
        self.kili_api_gateway = KiliAPIGateway(self.graphql_client, self.http_client)
        self.internal = InternalClientMethods(self.kili_api_gateway)
        self.llm = LlmClientMethods(self.kili_api_gateway)
        self.events = EventClientMethods(self.kili_api_gateway)

        if not skip_checks:
            api_key_use_cases = ApiKeyUseCases(self.kili_api_gateway)
            api_key_use_cases.check_expiry_of_key_is_close(api_key)

    # Domain API Namespaces - Lazy loaded properties
    @cached_property
    def assets_ns(self) -> AssetsNamespace:
        """Get the assets domain namespace.

        Returns:
            AssetsNamespace: Assets domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            assets_ns = kili.assets_ns
            ```
        """
        return AssetsNamespace(self, self.kili_api_gateway)

    @cached_property
    def labels_ns(self) -> LabelsNamespace:
        """Get the labels domain namespace.

        Returns:
            LabelsNamespace: Labels domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            labels_ns = kili.labels_ns
            ```
        """
        return LabelsNamespace(self, self.kili_api_gateway)

    @cached_property
    def projects_ns(self) -> ProjectsNamespace:
        """Get the projects domain namespace.

        Returns:
            ProjectsNamespace: Projects domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            projects_ns = kili.projects_ns
            ```
        """
        return ProjectsNamespace(self, self.kili_api_gateway)

    @cached_property
    def users_ns(self) -> UsersNamespace:
        """Get the users domain namespace.

        Returns:
            UsersNamespace: Users domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            users_ns = kili.users_ns
            ```
        """
        return UsersNamespace(self, self.kili_api_gateway)

    @cached_property
    def organizations_ns(self) -> OrganizationsNamespace:
        """Get the organizations domain namespace.

        Returns:
            OrganizationsNamespace: Organizations domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            organizations_ns = kili.organizations_ns
            ```
        """
        return OrganizationsNamespace(self, self.kili_api_gateway)

    @cached_property
    def issues_ns(self) -> IssuesNamespace:
        """Get the issues domain namespace.

        Returns:
            IssuesNamespace: Issues domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            issues_ns = kili.issues_ns
            ```
        """
        return IssuesNamespace(self, self.kili_api_gateway)

    @cached_property
    def notifications_ns(self) -> NotificationsNamespace:
        """Get the notifications domain namespace.

        Returns:
            NotificationsNamespace: Notifications domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            notifications_ns = kili.notifications_ns
            ```
        """
        return NotificationsNamespace(self, self.kili_api_gateway)

    @cached_property
    def tags_ns(self) -> TagsNamespace:
        """Get the tags domain namespace.

        Returns:
            TagsNamespace: Tags domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            tags_ns = kili.tags_ns
            ```
        """
        return TagsNamespace(self, self.kili_api_gateway)

    @cached_property
    def cloud_storage_ns(self) -> CloudStorageNamespace:
        """Get the cloud storage domain namespace.

        Returns:
            CloudStorageNamespace: Cloud storage domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            cloud_storage_ns = kili.cloud_storage_ns
            ```
        """
        return CloudStorageNamespace(self, self.kili_api_gateway)

    @cached_property
    def connections_ns(self) -> ConnectionsNamespace:
        """Get the connections domain namespace.

        Returns:
            ConnectionsNamespace: Connections domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            connections_ns = kili.connections_ns
            ```
        """
        return ConnectionsNamespace(self, self.kili_api_gateway)

    @cached_property
    def integrations_ns(self) -> IntegrationsNamespace:
        """Get the integrations domain namespace.

        Returns:
            IntegrationsNamespace: Integrations domain namespace with lazy loading

        Examples:
            ```python
            kili = Kili()
            # Namespace is instantiated on first access
            integrations_ns = kili.integrations_ns
            ```
        """
        return IntegrationsNamespace(self, self.kili_api_gateway)

    def __getattr__(self, name: str):
        """Handle dynamic namespace routing based on legacy mode.

        When legacy=False, routes clean namespace names to their _ns counterparts.
        When legacy=True, raises AttributeError for clean names to fall back to legacy methods.

        Args:
            name: The attribute name being accessed

        Returns:
            The appropriate namespace instance

        Raises:
            AttributeError: When the attribute is not a recognized namespace or
                          when trying to access clean names in legacy mode
        """
        # Mapping of clean names to _ns property names
        namespace_mapping = {
            "assets": "assets_ns",
            "labels": "labels_ns",
            "projects": "projects_ns",
            "users": "users_ns",
            "organizations": "organizations_ns",
            "issues": "issues_ns",
            "notifications": "notifications_ns",
            "tags": "tags_ns",
            "cloud_storage": "cloud_storage_ns",
            "connections": "connections_ns",
            "integrations": "integrations_ns",
        }

        # In non-legacy mode, route clean names to _ns properties
        if not self._legacy_mode and name in namespace_mapping:
            return getattr(self, namespace_mapping[name])

        # For legacy mode or unrecognized attributes, raise AttributeError
        # This allows legacy methods to be accessible through normal inheritance
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __getattribute__(self, name: str):
        """Control access to legacy methods based on legacy mode setting.

        When legacy=False, prevents access to legacy methods that conflict with
        domain namespace names, providing clear error messages.

        Args:
            name: The attribute name being accessed

        Returns:
            The requested attribute

        Raises:
            AttributeError: When trying to access legacy methods in non-legacy mode
        """
        # Get the attribute normally first
        attr = super().__getattribute__(name)

        # Check if we're in non-legacy mode and trying to access a legacy method
        # Use object.__getattribute__ to avoid recursion
        try:
            legacy_mode = object.__getattribute__(self, "_legacy_mode")
        except AttributeError:
            # If _legacy_mode is not set yet, default to legacy behavior
            legacy_mode = True

        if not legacy_mode:
            # Legacy method names that conflict with clean namespace names
            legacy_method_names = {
                "assets",
                "projects",
                "labels",
                "users",
                "organizations",
                "issues",
                "notifications",
                "tags",
                "cloud_storage",
            }

            # If it's a callable legacy method, check if it should be blocked
            if callable(attr) and name in legacy_method_names:
                # Check if this method comes from a legacy mixin class
                # by examining the method's __qualname__
                if hasattr(attr, "__func__") and hasattr(attr.__func__, "__qualname__"):
                    qualname = attr.__func__.__qualname__
                    if any(
                        mixin_name in qualname
                        for mixin_name in [
                            "AssetClientMethods",
                            "ProjectClientMethods",
                            "LabelClientMethods",
                            "UserClientMethods",
                            "OrganizationClientMethods",
                            "IssueClientMethods",
                            "NotificationClientMethods",
                            "TagClientMethods",
                            "CloudStorageClientMethods",
                        ]
                    ):
                        raise AttributeError(
                            f"Legacy method '{name}()' is not available when legacy=False. "
                            f"Use 'kili.{name}' (domain namespace) instead of 'kili.{name}()' (legacy method)."
                        )

        return attr
