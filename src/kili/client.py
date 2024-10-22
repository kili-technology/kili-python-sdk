"""Kili Python SDK client."""

import getpass
import logging
import os
import sys
import warnings
from typing import Dict, Optional, Union

from kili.adapters.authentification import is_api_key_valid
from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.core.graphql.graphql_client import GraphQLClient, GraphQLClientName
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

        Returns:
            Instance of the Kili client.

        Examples:
            ```python
            from kili.client import Kili

            kili = Kili()

            kili.assets()  # list your assets
            kili.labels()  # list your labels
            kili.projects()  # list your projects
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

        if not skip_checks:
            api_key_use_cases = ApiKeyUseCases(self.kili_api_gateway)
            api_key_use_cases.check_expiry_of_key_is_close(api_key)
