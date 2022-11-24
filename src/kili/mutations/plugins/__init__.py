"""Project mutations."""
from typing import Optional

from typeguard import typechecked

from kili.authentication import KiliAuth
from kili.services.plugins import (
    PluginUploader,
    activate_plugin,
    deactivate_plugin,
    delete_plugin,
)


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
    def upload_plugin(
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
            >>> kili.upload_plugin(file_path="./path/to/my/file.py")
        """

        return PluginUploader(self.auth, file_path, plugin_name, verbose).create_plugin()

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

        return activate_plugin(self.auth, plugin_name, project_id)

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

        return deactivate_plugin(self.auth, plugin_name, project_id)

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

        return delete_plugin(self.auth, plugin_name)

    @typechecked
    def update_plugin(
        self,
        file_path: str,
        plugin_name: str,
        verbose: bool = True,
    ):
        """Update a plugin with new code.

        Args:
            file_path : Path to your .py file
            plugin_name: Name of the plugin
            verbose: If false, minimal logs are displayed

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.update_plugin(plugin_name="my_plugin_name")
        """

        return PluginUploader(self.auth, file_path, plugin_name, verbose).update_plugin()
