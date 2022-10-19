"""Project mutations."""


from typing import Optional

from typeguard import typechecked

from kili.services.plugins import PluginUploader, activate_plugin, deactivate_plugin

from ...authentication import KiliAuth
from ...helpers import Compatible


class MutationsPlugins:
    """Set of Plugins mutations."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth: KiliAuth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @Compatible(endpoints=["v2"])
    @typechecked
    def upload_plugin_beta(
        self,
        file_path: str,
        plugin_name: Optional[str] = None,
        verbose: bool = True,
    ):
        # pylint: disable=line-too-long
        """Upload a plugin.

        Args:
            file_path : Path to your .py file
            plugin_name: name of your plugin, if not provided, it will be the name from your file
            verbose: If false, minimal logs are displayed

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.upload_plugin_beta(file_path="./path/to/my/file.py")
        """

        result = PluginUploader(self.auth, file_path, plugin_name, verbose).create_plugin()
        return result

    @Compatible(endpoints=["v2"])
    @typechecked
    def activate_plugin_on_project(
        self,
        plugin_name: str,
        project_id: str,
    ):
        # pylint: disable=line-too-long
        """Activate a plugin on a project.

        Args:
            plugin_name: Name of the plugin
            project_id: Identifier of the project
            verbose: If false, minimal logs are displayed

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.activate_plugin_on_project(plugin_name="my_plugin_name", project_id="my_project_id")
        """

        pretty_result = activate_plugin(self.auth, plugin_name, project_id)
        return pretty_result

    @Compatible(endpoints=["v2"])
    @typechecked
    def deactivate_plugin_on_project(
        self,
        plugin_name: str,
        project_id: str,
    ):
        # pylint: disable=line-too-long
        """Activate a plugin on a project.

        Args:
            plugin_name: Name of the plugin
            project_id: Identifier of the project
            verbose: If false, minimal logs are displayed

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.deactivate_plugin_on_project(plugin_name="my_plugin_name", project_id="my_project_id")
        """

        pretty_result = deactivate_plugin(self.auth, plugin_name, project_id)
        return pretty_result
