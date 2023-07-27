"""
This script permits to initialize the Kili Python SDK client.
"""
import os
from typing import Union

from kili.authentication import KiliAuth
from kili.exceptions import AuthenticationFailed
from kili.graphql.graphql_client import GraphQLClientName
from kili.internal import KiliInternal
from kili.mutations.asset import MutationsAsset
from kili.mutations.data_connection import MutationsDataConnection
from kili.mutations.issue import MutationsIssue
from kili.mutations.label import MutationsLabel
from kili.mutations.notification import MutationsNotification
from kili.mutations.plugins import MutationsPlugins
from kili.mutations.project import MutationsProject
from kili.mutations.project_version import MutationsProjectVersion
from kili.mutations.user import MutationsUser
from kili.project import Project
from kili.queries.api_key import QueriesApiKey
from kili.queries.asset import QueriesAsset
from kili.queries.data_connection import QueriesDataConnection
from kili.queries.data_integration import QueriesDataIntegration
from kili.queries.issue import QueriesIssue
from kili.queries.label import QueriesLabel
from kili.queries.notification import QueriesNotification
from kili.queries.organization import QueriesOrganization
from kili.queries.plugins import QueriesPlugins
from kili.queries.project import QueriesProject
from kili.queries.project_user import QueriesProjectUser
from kili.queries.project_version import QueriesProjectVersion
from kili.queries.user import QueriesUser
from kili.services.project import get_project
from kili.services.types import ProjectId
from kili.subscriptions.label import SubscriptionsLabel

from .helpers import deprecate


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
    """
    Kili Client.
    """

    def __init__(
        self,
        api_key=None,
        api_endpoint=None,
        verify: Union[bool, str] = True,
        client_name=GraphQLClientName.SDK,
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
                verify: Verify certificate (see request's documentation). Set to False on
                local deployment without SSL.
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
                ssl_verify=verify,
            )
            super().__init__(self.auth)
        except Exception as exception:
            exception_str = str(exception)
            if "b'Unauthorized'" in exception_str:
                raise AuthenticationFailed(api_key, api_endpoint) from exception
            raise exception

        self.internal = KiliInternal(self)

    @deprecate(
        msg="This method is deprecated. Use `kili.projects(project_id='<MY_PROJECT_ID>')` instead",
        removed_in="2.131",
    )
    def get_project(self, project_id: str) -> Project:
        """Return a project object corresponding to the project_id given.
        The returned project object inherit from many methods for project management

        Args:
            project_id: id of the project to return

        raise:
            NotFound if the given `project_id` does not correspond to an existing project
        """
        project = get_project(self.auth, project_id, ["inputType", "title"])
        return Project(
            client=self,
            project_id=ProjectId(project_id),
            input_type=project["inputType"],
            title=project["title"],
        )
