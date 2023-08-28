"""This script permits to initialize the Kili Python SDK client."""
import getpass
import logging
import os
import sys
import warnings
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional, Union

import requests

from kili import __version__
from kili.core.graphql import QueryOptions
from kili.core.graphql.graphql_client import GraphQLClient, GraphQLClientName
from kili.core.graphql.operations.api_key.queries import APIKeyQuery, APIKeyWhere
from kili.core.graphql.operations.user.queries import GQL_ME
from kili.entrypoints.mutations.asset import MutationsAsset
from kili.entrypoints.mutations.data_connection import MutationsDataConnection
from kili.entrypoints.mutations.issue import MutationsIssue
from kili.entrypoints.mutations.label import MutationsLabel
from kili.entrypoints.mutations.notification import MutationsNotification
from kili.entrypoints.mutations.plugins import MutationsPlugins
from kili.entrypoints.mutations.project import MutationsProject
from kili.entrypoints.mutations.project_version import MutationsProjectVersion
from kili.entrypoints.mutations.user import MutationsUser
from kili.entrypoints.queries.asset import QueriesAsset
from kili.entrypoints.queries.data_connection import QueriesDataConnection
from kili.entrypoints.queries.data_integration import QueriesDataIntegration
from kili.entrypoints.queries.issue import QueriesIssue
from kili.entrypoints.queries.label import QueriesLabel
from kili.entrypoints.queries.notification import QueriesNotification
from kili.entrypoints.queries.organization import QueriesOrganization
from kili.entrypoints.queries.plugins import QueriesPlugins
from kili.entrypoints.queries.project import QueriesProject
from kili.entrypoints.queries.project_user import QueriesProjectUser
from kili.entrypoints.queries.project_version import QueriesProjectVersion
from kili.entrypoints.queries.user import QueriesUser
from kili.entrypoints.subscriptions.label import SubscriptionsLabel
from kili.exceptions import AuthenticationFailed, UserNotFoundError
from kili.gateways.kili_api_gateway import KiliAPIGateway
from kili.presentation.client.internal import InternalClientMethods
from kili.presentation.client.issue import IssueClientMethods
from kili.utils.logcontext import LogContext, log_call

warnings.filterwarnings("default", module="kili", category=DeprecationWarning)


class FilterPoolFullWarning(logging.Filter):
    """Filter out the specific urllib3 warning related to the connection pool."""

    def filter(self, record) -> bool:
        """urllib3.connectionpool:Connection pool is full, discarding connection: ..."""
        return "Connection pool is full, discarding connection" not in record.getMessage()


logging.getLogger("urllib3.connectionpool").addFilter(FilterPoolFullWarning())


class Kili(  # pylint: disable=too-many-ancestors,too-many-instance-attributes
    MutationsAsset,
    MutationsDataConnection,
    MutationsIssue,
    MutationsLabel,
    MutationsNotification,
    MutationsPlugins,
    MutationsProject,
    MutationsProjectVersion,
    MutationsUser,
    QueriesAsset,
    QueriesDataConnection,
    QueriesDataIntegration,
    QueriesIssue,
    QueriesLabel,
    QueriesNotification,
    QueriesOrganization,
    QueriesPlugins,
    QueriesProject,
    QueriesProjectUser,
    QueriesProjectVersion,
    QueriesUser,
    SubscriptionsLabel,
    IssueClientMethods,
):
    """Kili Client."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        verify: Union[bool, str] = True,
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

        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.verify = verify
        self.client_name = client_name
        self.graphql_client_params = graphql_client_params

        skip_checks = os.getenv("KILI_SDK_SKIP_CHECKS") is not None

        self.http_client = requests.Session()
        self.http_client.verify = verify

        if not skip_checks and not self._is_api_key_valid():
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
            **(graphql_client_params or {}),  # type: ignore
        )

        self.kili_api_gateway = KiliAPIGateway(self.graphql_client, self.http_client)

        if not skip_checks:
            api_key_query = APIKeyQuery(self.graphql_client, self.http_client)
            self._check_expiry_of_key_is_close(api_key_query, self.api_key)

        self.internal = InternalClientMethods(self)

    @log_call
    def _is_api_key_valid(self) -> bool:
        """Check that the api_key provided is valid."""
        response = self.http_client.post(
            url=self.api_endpoint,
            data='{"query":"{ me { id email } }"}',
            timeout=30,
            headers={
                "Authorization": f"X-API-Key: {self.api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "apollographql-client-name": self.client_name.value,
                "apollographql-client-version": __version__,
                **LogContext(),
            },
        )
        return response.status_code == 200 and "email" in response.text and "id" in response.text

    def _get_kili_app_version(self) -> Optional[str]:
        """Get the version of the Kili app server.

        Returns None if the version cannot be retrieved.
        """
        url = self.api_endpoint.replace("/graphql", "/version")
        response = self.http_client.get(url, timeout=30)
        if response.status_code == 200 and '"version":' in response.text:
            response_json = response.json()
            version = response_json["version"]
            return version
        return None

    @staticmethod
    def _check_expiry_of_key_is_close(api_key_query: Callable, api_key: str) -> None:
        """Check that the expiration date of the api_key is not too close."""
        warn_days = 30

        api_keys = api_key_query(
            fields=["expiryDate"],
            where=APIKeyWhere(api_key=api_key),
            options=QueryOptions(disable_tqdm=True),
        )

        key_expiry = datetime.strptime(next(api_keys)["expiryDate"], r"%Y-%m-%dT%H:%M:%S.%fZ")
        key_remaining_time = key_expiry - datetime.now()
        key_soon_deprecated = key_remaining_time < timedelta(days=warn_days)
        if key_soon_deprecated:
            message = f"""
                Your api key will be deprecated on {key_expiry:%Y-%m-%d}.
                You should generate a new one on My account > API KEY."""
            warnings.warn(message, UserWarning, stacklevel=2)

    def get_user(self) -> Dict:
        """Get the current user from the api_key provided."""
        result = self.graphql_client.execute(GQL_ME)
        user = self.format_result("data", result)
        if user is None or user["id"] is None or user["email"] is None:
            raise UserNotFoundError("No user attached to the API key was found")
        return user
