"""
This script permits to initialize the Kili Playground client.
"""
import os

from kili.mutations.api_key import MutationsApiKey
from kili.mutations.asset import MutationsAsset
from kili.mutations.dataset import MutationsDataset
from kili.mutations.dataset_asset import MutationsDatasetAsset
from kili.mutations.label import MutationsLabel
from kili.mutations.notification import MutationsNotification
from kili.mutations.organization import MutationsOrganization
from kili.mutations.project import MutationsProject
from kili.mutations.project_version import MutationsProjectVersion
from kili.mutations.user import MutationsUser
from kili.queries.api_key import QueriesApiKey
from kili.queries.asset import QueriesAsset
from kili.queries.dataset import QueriesDataset
from kili.queries.dataset_asset import QueriesDatasetAsset
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
        MutationsDataset,
        MutationsDatasetAsset,
        MutationsLabel,
        MutationsNotification,
        MutationsOrganization,
        MutationsProject,
        MutationsProjectVersion,
        MutationsUser,
        QueriesApiKey,
        QueriesAsset,
        QueriesDataset,
        QueriesDatasetAsset,
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
        Parameters
        ----------
        api_key:
            User API key generated from https://cloud.kili-technology.com/label/my-account/api-key

        api_endpoint : str
            Recipient of the HTTP operation

        verify : bool
            Verify certificate. Set to False on local deployment without SSL.

        Returns
        -------
        Kili object
        Object container your API session.
        Then, list:
        - your assets with: kili.assets()
        - your labels with: kili.labels()
        - your projects with: kili.projects()
        """
        self.auth = KiliAuth(
            api_key=api_key, api_endpoint=api_endpoint, verify=verify)
        super().__init__(self.auth)
