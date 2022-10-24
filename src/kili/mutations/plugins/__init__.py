"""Project mutations."""


from datetime import datetime
from typing import Optional

from typeguard import typechecked

from kili.services.plugins import (
    PluginUploader,
    activate_plugin,
    deactivate_plugin,
    delete_plugin,
    get_logs,
)

from ...authentication import KiliAuth


class MutationsPlugins:
    """Set of Plugins mutations."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth: KiliAuth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @typechecked
    def upload_plugin_beta(
        self,
        file_path: str,
        plugin_name: Optional[str] = None,
        verbose: bool = True,
    ):
        # pylint: disable=line-too-long
        """Uploads a plugin.

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

    @typechecked
    def activate_plugin_on_project(
        self,
        plugin_name: str,
        project_id: str,
    ):
        # pylint: disable=line-too-long
        """Activates a plugin on a project.

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

    @typechecked
    def deactivate_plugin_on_project(
        self,
        plugin_name: str,
        project_id: str,
    ):
        # pylint: disable=line-too-long
        """Activates a plugin on a project.

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

    @typechecked
    def delete_plugin(
        self,
        plugin_name: str,
    ):
        # pylint: disable=line-too-long
        """Deletes a plugin.

        Args:
            plugin_name: Name of the plugin
            verbose: If false, minimal logs are displayed

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.delete_plugin(plugin_name="my_plugin_name")
        """

        pretty_result = delete_plugin(self.auth, plugin_name)
        return pretty_result

    @typechecked
    def get_plugin_logs(
        self,
        project_id: str,
        plugin_name: str,
        start_date: datetime,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
    ):
        # pylint: disable=line-too-long
        """Get paginated logs of a plugin on a project.

        Args:
            project_id: Identifier of the project
            plugin_name: Name of the plugin
            start_date: Datetime used to get the logs from
            limit: Limit for pagination, if not provided, it will be 100
            skip: Skip for pagination, if not provided, it will be 0

        Returns:
            A result array which contains the logs of the plugin,
                or an error message.

        Examples:
            >>> kili.get_plugin_logs(project_id="my_project_id", plugin_name="my_plugin_name", start_date="1970/01/01")
        """

        plugin = {"project_id": project_id, "plugin_name": plugin_name}

        pretty_result = get_logs(self.auth, plugin, start_date, limit, skip)
        return pretty_result
