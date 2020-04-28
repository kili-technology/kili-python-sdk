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

from .helpers import deprecate


class Playground(object):

    def __init__(self, auth=None):
        """Create an instance of KiliPlayground."""
        self.auth = auth

    # Mutations Asset

    def delete_assets_by_external_id(self, **kwargs):
        return kili.mutations.asset.delete_assets_by_external_id(self.auth.client, **kwargs)

    def append_many_to_dataset(self, **kwargs):
        return kili.mutations.asset.append_many_to_dataset(self.auth.client, **kwargs)

    def update_properties_in_asset(self, **kwargs):
        return kili.mutations.asset.update_properties_in_asset(self.auth.client, **kwargs)

    def delete_many_from_dataset(self, **kwargs):
        return kili.mutations.asset.delete_many_from_dataset(self.auth.client, **kwargs)

    # Mutations Label

    def create_predictions(self, **kwargs):
        return kili.mutations.label.create_predictions(self.auth.client, **kwargs)

    def append_to_labels(self, **kwargs):
        return kili.mutations.label.append_to_labels(self.auth.client, **kwargs)

    def update_properties_in_label(self, **kwargs):
        return kili.mutations.label.update_properties_in_label(self.auth.client, **kwargs)

    def create_honeypot(self, **kwargs):
        return kili.mutations.label.create_honeypot(self.auth.client, **kwargs)

    # Mutations Organization

    def create_organization(self, **kwargs):
        return kili.mutations.organization.create_organization(self.auth.client, **kwargs)

    def update_properties_in_organization(self, **kwargs):
        return kili.mutations.organization.update_properties_in_organization(self.auth.client, **kwargs)

    # Mutations Project

    def append_to_roles(self, **kwargs):
        return kili.mutations.project.append_to_roles(self.auth.client, **kwargs)

    def update_properties_in_project(self, **kwargs):
        return kili.mutations.project.update_properties_in_project(self.auth.client, **kwargs)

    def create_empty_project(self, **kwargs):
        return kili.mutations.project.create_empty_project(self.auth.client, **kwargs)

    def update_project(self, **kwargs):
        return kili.mutations.project.update_project(self.auth.client, **kwargs)

    def update_properties_in_role(self, **kwargs):
        return kili.mutations.project.update_properties_in_role(self.auth.client, **kwargs)

    def delete_from_roles(self, **kwargs):
        return kili.mutations.project.delete_from_roles(self.auth.client, **kwargs)

    def update_properties_in_project_user(self, **kwargs):
        return kili.mutations.project.update_properties_in_project_user(self.auth.client, **kwargs)

    def force_project_kpis(self, **kwargs):
        return kili.mutations.project.force_project_kpis(self.auth.client, **kwargs)

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

    # Mutations User

    def create_user(self, **kwargs):
        return kili.mutations.user.create_user(self.auth.client, **kwargs)

    def create_user_from_email_if_not_exists(self, **kwargs):
        return kili.mutations.user.create_user_from_email_if_not_exists(self.auth.client, **kwargs)

    def update_password(self, **kwargs):
        return kili.mutations.user.update_password(self.auth.client, **kwargs)

    def reset_password(self, **kwargs):
        return kili.mutations.user.reset_password(self.auth.client, **kwargs)

    def update_properties_in_user(self, **kwargs):
        return kili.mutations.user.update_properties_in_user(self.auth.client, **kwargs)

    # Queries Asset

    def assets(self, **kwargs):
        return kili.queries.asset.assets(self.auth.client, **kwargs)

    def get_asset(self, **kwargs):
        return kili.queries.asset.get_asset(self.auth.client, **kwargs)

    def get_assets(self, **kwargs):
        return kili.queries.asset.get_assets(self.auth.client, **kwargs)

    def get_assets_by_external_id(self, **kwargs):
        return kili.queries.asset.get_assets_by_external_id(self.auth.client, **kwargs)

    def get_next_asset_from_label(self, **kwargs):
        return kili.queries.asset.get_next_asset_from_label(self.auth.client, **kwargs)

    def get_next_asset_from_project(self, **kwargs):
        return kili.queries.asset.get_next_asset_from_project(self.auth.client, **kwargs)

    # Queries Label

    def get_label(self, **kwargs):
        return kili.queries.label.get_label(self.auth.client, **kwargs)

    def get_latest_labels_for_user(self, **kwargs):
        return kili.queries.label.get_latest_labels_for_user(self.auth.client, **kwargs)

    def get_latest_labels(self, **kwargs):
        return kili.queries.label.get_latest_labels(self.auth.client, **kwargs)

    def export_labels_as_df(self, **kwargs):
        return kili.queries.label.export_labels_as_df(self.auth.client, **kwargs)

    # Queries Project

    def get_projects(self, **kwargs):
        return kili.queries.project.get_projects(self.auth.client, **kwargs)

    def get_project(self, **kwargs):
        return kili.queries.project.get_project(self.auth.client, **kwargs)

    # Queries Tool

    @deprecate(
        """
        This function is deprecated. Tools used to describe an interface. They are now called jsonInterface.
        To update jsonInterface, use:
            > playground.update_properties_in_project(project_id=project_id, json_interface=json_interface)
        """)
    def get_tools(self, **kwargs):
        return None

    # Queries User

    def get_user(self, **kwargs):
        return kili.queries.user.get_user(self.auth.client, **kwargs)

    def users(self, **kwargs):
        return kili.queries.user.users(self.auth.client, **kwargs)

    # Queries ProjectUser

    def project_users(self, **kwargs):
        return kili.queries.project_user.project_users(self.auth.client, **kwargs)

    # Subscriptions Label

    def label_created_or_updated(self, **kwargs):
        return kili.subscriptions.label.label_created_or_updated(self.auth.client, **kwargs)


if __name__ == '__main__':
    """ Example of usage """
    from kili.authentication import KiliAuth
    from kili.playground import Playground
    kauth = KiliAuth()
    playground = Playground(kauth)
    assets = playground.assets(project_id="first-project")
    print(assets)
