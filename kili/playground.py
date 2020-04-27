import kili.mutations.asset
import kili.mutations.label
import kili.mutations.organization
import kili.mutations.project
import kili.mutations.user
import kili.queries.asset
import kili.queries.label
import kili.queries.project
import kili.queries.project_user
import kili.queries.user
import kili.subscriptions.label

from kili.helpers import deprecate


class Playground(
    kili.mutations.asset.MutationsAssets,
    kili.mutations.label.MutationsLabel,
    kili.mutations.organization.MutationsOrganization,
    kili.mutations.project.MutationsProject,
    kili.mutations.user.MutationsUser,
    kili.queries.asset.QueriesAsset,
    kili.queries.label.QueriesLabel,
    kili.queries.project.QueriesProject,
    kili.queries.project_user.QueriesProjectUser,
    kili.queries.user.QueriesUser,
    kili.subscriptions.label.SubscriptionsLabel):

    def __init__(self, auth=None):
        """Create an instance of KiliPlayground."""
        self.auth = auth
        super().__init__(auth)

    # Mutations Tool

    @deprecate(
        """
        This function is deprecated. Tools used to describe an interface. They are now called jsonInterface.
        To update jsonInterface, use:
            > playground.update_properties_in_project(project_id=project_id, json_interface=json_interface)
        """)
    def update_tool(self, **kwargs):
        return None

    @deprecate(
        """
        This function is deprecated. Tools used to describe an interface. They are now called jsonInterface.
        To update jsonInterface, use:
            > playground.update_properties_in_project(project_id=project_id, json_interface=json_interface)
        """)
    def append_to_tools(self, **kwargs):
        return None

    # Queries Tool

    @deprecate(
        """
        This function is deprecated. Tools used to describe an interface. They are now called jsonInterface.
        To update jsonInterface, use:
            > playground.update_properties_in_project(project_id=project_id, json_interface=json_interface)
        """)
    def get_tools(self, **kwargs):
        return None


if __name__ == '__main__':
    """ Example of usage """
    from kili.authentication import KiliAuth
    from kili.playground import Playground
    kauth = KiliAuth()
    playground = Playground(kauth)
    assets = playground.export_assets(project_id="first-project")
    print(assets)
