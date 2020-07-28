import kili.mutations.asset
import kili.mutations.label
import kili.mutations.notification
import kili.mutations.organization
import kili.mutations.project
import kili.mutations.user
import kili.queries.asset
import kili.queries.label
import kili.queries.organization
import kili.queries.project
import kili.queries.project_user
import kili.queries.user
import kili.subscriptions.label
from kili.constants import NO_ACCESS_RIGHT

from kili.helpers import deprecate


class Playground(
        kili.mutations.asset.MutationsAsset,
        kili.mutations.label.MutationsLabel,
        kili.mutations.notification.MutationsNotification,
        kili.mutations.organization.MutationsOrganization,
        kili.mutations.project.MutationsProject,
        kili.mutations.user.MutationsUser,
        kili.queries.asset.QueriesAsset,
        kili.queries.label.QueriesLabel,
        kili.queries.organization.QueriesOrganization,
        kili.queries.project.QueriesProject,
        kili.queries.project_user.QueriesProjectUser,
        kili.queries.user.QueriesUser,
        kili.subscriptions.label.SubscriptionsLabel):

    def __init__(self, auth=None):
        """Create an instance of KiliPlayground."""
        self.auth = auth
        super().__init__(auth)


if __name__ == '__main__':
    """ Example of usage """
    from kili.authentication import KiliAuth
    from kili.playground import Playground
    kauth = KiliAuth()
    playground = Playground(kauth)
    assets = playground.assets(project_id="first-project")
    print(assets)
