"""This script permits to initialize the Kili Python SDK client."""
import os

from kili.core.authentication import KiliAuth
from kili.core.graphql.graphql_client import GraphQLClientName
from kili.entrypoints.mutations.asset import MutationsAsset
from kili.entrypoints.mutations.data_connection import MutationsDataConnection
from kili.entrypoints.mutations.issue import MutationsIssue
from kili.entrypoints.mutations.label import MutationsLabel
from kili.entrypoints.mutations.notification import MutationsNotification
from kili.entrypoints.mutations.plugins import MutationsPlugins
from kili.entrypoints.mutations.project import MutationsProject
from kili.entrypoints.mutations.project_version import MutationsProjectVersion
from kili.entrypoints.mutations.user import MutationsUser
from kili.entrypoints.queries.api_key import QueriesApiKey
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
from kili.exceptions import AuthenticationFailed
from kili.internal import KiliInternal


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
    QueriesApiKey,
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

    def __init__(
        self, api_key=None, api_endpoint=None, verify=True, client_name=GraphQLClientName.SDK
    ):
        """
        Args:
            api_key: User API key generated
                from https://cloud.kili-technology.com/label/my-account/api-key
                Default to  KILI_API_KEY environment variable).
                If not passed, requires the KILI_API_KEY environment variable to be set.
            api_endpoint: Recipient of the HTTP operation
                Default to  KILI_API_ENDPOINT environment variable).
                If not passed, default to Kili SaaS:
                'https://cloud.kili-technology.com/api/label/v2/graphql'
            verify: Verify certificate. Set to False on local deployment without SSL.
            client_name: For internal use only.
                Define the name of the graphQL client whith which graphQL calls will be sent.

        Returns:
            Object container your API session

        Examples:
            list:
                - your assets with: `kili.assets()`
                - your labels with: `kili.labels()`
                - your projects with: `kili.projects()`
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
        try:
            self.auth = KiliAuth(
                api_key=api_key,
                api_endpoint=api_endpoint,
                client_name=client_name,
                verify=verify,
            )
            super().__init__(self.auth)
        except Exception as exception:
            exception_str = str(exception)
            if "b'Unauthorized'" in exception_str:
                raise AuthenticationFailed(api_key, api_endpoint) from exception
            raise exception

        self.internal = KiliInternal(self)
