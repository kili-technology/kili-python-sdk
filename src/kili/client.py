"""This script permits to initialize the Kili Python SDK client."""
import os
import warnings
from datetime import datetime, timedelta
from typing import Dict, Optional

import requests

from kili import __version__
from kili.core.graphql import QueryOptions
from kili.core.graphql.graphql_client import GraphQLClient, GraphQLClientName
from kili.core.graphql.operations.api_key.queries import APIKeyQuery, APIKeyWhere
from kili.core.graphql.operations.user.queries import GQL_ME
from kili.core.helpers import format_result
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
from kili.internal import KiliInternal

warnings.filterwarnings("default", module="kili", category=DeprecationWarning)


class Kili(  # pylint: disable=too-many-ancestors
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
):
    """Kili Client."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        verify: bool = True,
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
            verify: Verify certificate. Set to False on local deployment without SSL.
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
        if api_key is None:
            api_key = os.getenv("KILI_API_KEY")

        if api_endpoint is None:
            api_endpoint = os.getenv(
                "KILI_API_ENDPOINT",
                "https://cloud.kili-technology.com/api/label/v2/graphql",
            )

        if api_key is None:
            raise AuthenticationFailed(api_key, api_endpoint)

        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.verify = verify
        self.client_name = client_name
        self.graphql_client_params = graphql_client_params

        skip_checks = os.environ.get("KILI_SDK_SKIP_CHECKS", None) is not None

        if not skip_checks:
            self._check_api_key_valid()

        self.graphql_client = GraphQLClient(
            endpoint=api_endpoint,
            api_key=api_key,
            client_name=client_name,
            verify=self.verify,
            **(graphql_client_params or {}),  # type: ignore
        )

        if not skip_checks:
            self._check_expiry_of_key_is_close()

        self.internal = KiliInternal(self)

    def _check_api_key_valid(self) -> None:
        """Check that the api_key provided is valid."""
        response = requests.post(
            url=self.api_endpoint,
            data='{"query":"{ me { id email } }"}',
            verify=self.verify,
            timeout=30,
            headers={
                "Authorization": f"X-API-Key: {self.api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "apollographql-client-name": self.client_name.value,
                "apollographql-client-version": __version__,
            },
        )
        if response.status_code == 200 and "email" in response.text and "id" in response.text:
            return

        raise AuthenticationFailed(
            api_key=self.api_key,
            api_endpoint=self.api_endpoint,
            error_msg=(
                "Cannot check API key validity: status_code"
                f" {response.status_code}\n\n{response.text}"
            ),
        )

    def _check_expiry_of_key_is_close(self) -> None:
        """Check that the expiration date of the api_key is not too close."""
        warn_days = 30

        api_keys = APIKeyQuery(self.graphql_client)(
            fields=["expiryDate"],
            where=APIKeyWhere(api_key=self.api_key),
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
        user = format_result("data", result)
        if user is None or user["id"] is None or user["email"] is None:
            raise UserNotFoundError("No user attached to the API key was found")
        return user
