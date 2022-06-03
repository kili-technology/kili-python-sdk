"""
This script permits to initialize the Kili Python SDK client.
"""
import os

from kili.exceptions import NotFound
from kili.mutations.api_key import MutationsApiKey
from kili.mutations.asset import MutationsAsset
from kili.mutations.label import MutationsLabel
from kili.mutations.notification import MutationsNotification
from kili.mutations.organization import MutationsOrganization
from kili.mutations.project import MutationsProject
from kili.mutations.project_version import MutationsProjectVersion
from kili.mutations.user import MutationsUser
from kili.project import Project
from kili.queries.api_key import QueriesApiKey
from kili.queries.asset import QueriesAsset
from kili.queries.issue import QueriesIssue
from kili.queries.label import QueriesLabel
from kili.queries.lock import QueriesLock
from kili.queries.organization import QueriesOrganization
from kili.queries.notification import QueriesNotification
from kili.queries.project import QueriesProject
from kili.queries.project_user import QueriesProjectUser
from kili.queries.project_version import QueriesProjectVersion
from kili.queries.user import QueriesUser
from kili.subscriptions.label import SubscriptionsLabel


from kili.authentication import KiliAuth


class Kili(  # pylint: disable=too-many-ancestors
        MutationsApiKey,
        MutationsAsset,
        MutationsLabel,
        MutationsNotification,
        MutationsOrganization,
        MutationsProject,
        MutationsProjectVersion,
        MutationsUser,
        QueriesApiKey,
        QueriesAsset,
        QueriesIssue,
        QueriesLabel,
        QueriesLock,
        QueriesOrganization,
        QueriesNotification,
        QueriesProject,
        QueriesProjectUser,
        QueriesProjectVersion,
        QueriesUser,
        SubscriptionsLabel):
    """
    Kili Client.
    """

    def __init__(self, api_key=os.getenv('KILI_API_KEY'),
                 api_endpoint='https://cloud.kili-technology.com/api/label/v2/graphql',
                 verify=True):
        """
        Args:
            api_key: User API key generated
                from https://cloud.kili-technology.com/label/my-account/api-key
            api_endpoint: Recipient of the HTTP operation
            verify: Verify certificate. Set to False on local deployment without SSL.

        Returns:
            Object container your API session

        Examples:
            list:
                - your assets with: `kili.assets()`
                - your labels with: `kili.labels()`
                - your projects with: `kili.projects()`
        """
        self.auth = KiliAuth(
            api_key=api_key, api_endpoint=api_endpoint, verify=verify)
        super().__init__(self.auth)

    def get_project(self, project_id: str) -> Project:
        """Return a project object corresponding to the project_id given.
        The returned project object inherit from many methods for project management

        Args:
            project_id: id of the project to return

        raise:
            NotFound if the given `project_id` does not correspond to an existing project
        """
        query = self.projects(project_id=project_id,
                              disable_tqdm=True, fields=['inputType', 'title'])

        if len(query) == 0:
            raise NotFound(str(project_id))
        project_fields = query[0]
        title = project_fields['title']
        input_type = project_fields['inputType']
        return Project(client=self, project_id=project_id, input_type=input_type, title=title)
