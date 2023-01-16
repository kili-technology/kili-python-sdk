"""Project mutations."""
from typing import Optional

from typeguard import typechecked

from kili.authentication import KiliAuth
from kili.services.plugins import (
    PluginUploader,
    WebhookUploader,
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
        plugin_path: Optional[str] = None,
        plugin_name: Optional[str] = None,
        verbose: bool = True,
        **kwargs
    ):
        # pylint: disable=line-too-long
        """Uploads a plugin.

        Args:
            plugin_path : Path to your plugin. Either a folder containing a main.py (mandatory) and a requirements.txt (optional) or a .py file
            plugin_name: name of your plugin, if not provided, it will be the name from your file
            verbose: If false, minimal logs are displayed

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.upload_plugin(plugin_path="./path/to/my/file.py")
        """

        if kwargs.get("file_path"):
            raise TypeError(
                '"file_path" has been deprecated for "plugin_path", please use "plugin_path" instead'
            )

        if not plugin_path:
            raise TypeError('"plugin_path is nullish, please provide a value')

        return PluginUploader(self.auth, plugin_path, plugin_name, verbose).create_plugin()

    @typechecked
    def create_webhook(
        self,
        webhook_url: str,
        plugin_name: str,
        header: Optional[str] = None,
        verbose: bool = True,
    ):
        # pylint: disable=line-too-long
        """Create a webhook linked to Kili's events.

        Args:
            webhook_url: URL receiving post requests on events on Kili
            plugin_name: name of your plugin
            header: Authorization header to access the routes
            verbose: If false, minimal logs are displayed

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.create_webhook(webhook_url='https://my-custom-url-publicly-accessible/', plugin_name='my webhook', header='...')
        """

        return WebhookUploader(
            self.auth, webhook_url, plugin_name, header, verbose
        ).create_webhook()

    @typechecked
    def update_webhook(
        self,
        new_webhook_url: str,
        plugin_name: str,
        new_header: Optional[str] = None,
        verbose: bool = True,
    ):
        # pylint: disable=line-too-long
        """Update a webhook linked to Kili's events.

        Args:
            new_webhook_url: New URL receiving post requests on events on Kili
            plugin_name: name of your plugin
            new_header: Authorization header to access the routes
            verbose: If false, minimal logs are displayed

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.update_webhook(webhook_url='https://my-custom-url-publicly-accessible/', plugin_name='my webhook', header='...')
        """

        return WebhookUploader(
            self.auth, new_webhook_url, plugin_name, new_header, verbose
        ).update_webhook()

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
        plugin_path: Optional[str] = None,
        plugin_name: Optional[str] = None,
        verbose: bool = True,
        **kwargs
    ):
        """Update a plugin with new code.

        Args:
            plugin_path : Path to your plugin. Either:
             - a folder containing a main.py (mandatory) and a requirements.txt (optional)
             - a .py file
            plugin_name: Name of the plugin
            verbose: If false, minimal logs are displayed

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.update_plugin(plugin_name="my_plugin_name")
        """

        if kwargs.get("file_path"):
            raise TypeError(
                """ "file_path" has been deprecated for "plugin_path",
                please use "plugin_path" instead"""
            )

        if not plugin_path:
            raise TypeError('"plugin_path is nullish, please provide a value')

        if not plugin_name:
            raise TypeError('"plugin_name is nullish, please provide a value')

        return PluginUploader(self.auth, plugin_path, plugin_name, verbose).update_plugin()
