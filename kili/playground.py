import kili.mutations.asset
import kili.mutations.dataset_asset
import kili.mutations.label
import kili.mutations.notification
import kili.mutations.organization
import kili.mutations.project
import kili.mutations.project_version
import kili.mutations.user
import kili.queries.asset
import kili.queries.dataset_asset
import kili.queries.issue
import kili.queries.label
import kili.queries.lock
import kili.queries.organization
import kili.queries.notification
import kili.queries.project
import kili.queries.project_user
import kili.queries.project_version
import kili.queries.user
import kili.subscriptions.label
from kili.constants import NO_ACCESS_RIGHT

from kili.helpers import deprecate


@deprecate(
    """
        This method is deprecated since: 12/04/2021.
        This method will be removed after: 12/05/2021.
        Use instead:
            > from kili import Kili
            > kili = Kili(api_key=api_key)
            > kili.assets()
        """)
class Playground(
        kili.mutations.asset.MutationsAsset,
        kili.mutations.dataset_asset.MutationsDatasetAsset,
        kili.mutations.label.MutationsLabel,
        kili.mutations.notification.MutationsNotification,
        kili.mutations.organization.MutationsOrganization,
        kili.mutations.project.MutationsProject,
        kili.mutations.project_version.MutationsProjectVersion,
        kili.mutations.user.MutationsUser,
        kili.queries.asset.QueriesAsset,
        kili.queries.dataset_asset.QueriesDatasetAsset,
        kili.queries.issue.QueriesIssue,
        kili.queries.label.QueriesLabel,
        kili.queries.lock.QueriesLock,
        kili.queries.organization.QueriesOrganization,
        kili.queries.notification.QueriesNotification,
        kili.queries.project.QueriesProject,
        kili.queries.project_user.QueriesProjectUser,
        kili.queries.project_version.QueriesProjectVersion,
        kili.queries.user.QueriesUser,
        kili.subscriptions.label.SubscriptionsLabel):

    def __init__(self, auth=None, playground=None):
        """Create an instance of KiliPlayground."""
        self.auth = auth
        super().__init__(auth)
