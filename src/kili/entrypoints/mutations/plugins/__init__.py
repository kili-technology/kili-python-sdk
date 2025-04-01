"""Project mutations."""

from typing import List, Optional

from typeguard import typechecked
from typing_extensions import LiteralString

from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.services.plugins import (
    PluginUploader,
    WebhookUploader,
    activate_plugin,
    deactivate_plugin,
    delete_plugin,
)
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class MutationsPlugins(BaseOperationEntrypointMixin):
    """Set of Plugins mutations."""

    @typechecked
    def upload_plugin(
        self,
        plugin_path: Optional[str] = None,
        plugin_name: Optional[str] = None,
        verbose: bool = True,
        event_matcher: Optional[List[str]] = None,
        **kwargs,  # pylint: disable=missing-param-doc
    ) -> LiteralString:
        """Uploads a plugin.

        Args:
            plugin_path: Path to your plugin. Either:

                - a folder containing a main.py (mandatory) and a requirements.txt (optional)
                - a .py file
            plugin_name: name of your plugin, if not provided, it will be the name from your file
            event_matcher: List of events for which the plugin should be called.
            verbose: If false, minimal logs are displayed

        Returns:
            A string which indicates if the mutation was successful, or an error message.

        Examples:
            >>> kili.upload_plugin(plugin_path="./path/to/my/folder")
            >>> kili.upload_plugin(plugin_path="./path/to/my/file.py")
        """
        if kwargs.get("file_path"):
            raise TypeError(
                '"file_path" has been deprecated for "plugin_path", please use "plugin_path"'
                " instead"
            )

        if not plugin_path:
            raise TypeError('"plugin_path is nullish, please provide a value')

        return PluginUploader(
            self,  # pyright: ignore[reportGeneralTypeIssues]
            plugin_path,
            plugin_name,
            verbose,
            self.http_client,
            event_matcher,
        ).create_plugin()

    @typechecked
    def create_webhook(
        self,
        webhook_url: str,
        plugin_name: str,
        header: Optional[str] = None,
        verbose: bool = True,
        handler_types: Optional[List[str]] = None,
        event_matcher: Optional[List[str]] = None,
    ) -> str:
        # pylint: disable=line-too-long,too-many-arguments
        """Create a webhook linked to Kili's events.

        For a complete example, refer to the notebook `webhooks_example` on kili repo.

        Args:
            webhook_url: URL receiving post requests on events on Kili. The payload will be the following:

                - eventType: the type of event called
                - logPayload:
                    - runId: a unique identifier of the run for observability
                    - projectId: the Kili project the webhook is called on
                - payload: the event produced, for example for `onSubmit` event:
                    - label: the label produced
                    - asset_id: the asset on which the label is produced
            plugin_name: name of your plugin
            header: Authorization header to access the routes
            verbose: If false, minimal logs are displayed
            handler_types: List of actions for which the webhook should be called.
                Possible variants: `onSubmit`, `onReview`.
                By default, is [`onSubmit`, `onReview`].
            event_matcher: List of events for which the webhook should be called.

        Returns:
            A string which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.create_webhook(webhook_url='https://my-custom-url-publicly-accessible/', plugin_name='my webhook', header='...')
        """
        return WebhookUploader(
            self,  # pyright: ignore[reportGeneralTypeIssues]
            webhook_url,
            plugin_name,
            header,
            verbose,
            handler_types,
            event_matcher,
        ).create_webhook()

    @typechecked
    def update_webhook(
        self,
        new_webhook_url: str,
        plugin_name: str,
        new_header: Optional[str] = None,
        verbose: bool = True,
        handler_types: Optional[List[str]] = None,
        event_matcher: Optional[List[str]] = None,
    ) -> str:
        # pylint: disable=line-too-long,too-many-arguments
        """Update a webhook linked to Kili's events.

        For a complete example, refer to the notebook `webhooks_example` on kili repo.

        Args:
            new_webhook_url: New URL receiving post requests on events on Kili. See `create_webhook` for the payload description
            plugin_name: name of your plugin
            new_header: Authorization header to access the routes
            verbose: If false, minimal logs are displayed
            handler_types: List of actions for which the webhook should be called.
                Possible variants: `onSubmit`, `onReview`.
                By default, is [`onSubmit`, `onReview`]
            event_matcher: List of events for which the webhook should be called.

        Returns:
            A string which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.update_webhook(webhook_url='https://my-custom-url-publicly-accessible/', plugin_name='my webhook', header='...')
        """
        return WebhookUploader(
            self,  # pyright: ignore[reportGeneralTypeIssues]
            new_webhook_url,
            plugin_name,
            new_header,
            verbose,
            handler_types,
            event_matcher,
        ).update_webhook()

    @typechecked
    def activate_plugin_on_project(self, plugin_name: str, project_id: str) -> Optional[str]:
        """Activates a plugin on a project.

        Args:
            plugin_name: Name of the plugin
            project_id: Identifier of the project

        Returns:
            A string which indicates if the mutation was successful, or an error message.

        Examples:
            >>> kili.activate_plugin_on_project(plugin_name="my_plugin_name", project_id="my_project_id")
        """
        return activate_plugin(self, plugin_name, project_id)

    @typechecked
    def deactivate_plugin_on_project(self, plugin_name: str, project_id: str) -> str:
        """Activates a plugin on a project.

        Args:
            plugin_name: Name of the plugin
            project_id: Identifier of the project

        Returns:
            A string which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.deactivate_plugin_on_project(plugin_name="my_plugin_name", project_id="my_project_id")
        """
        return deactivate_plugin(self, plugin_name, project_id)

    @typechecked
    def delete_plugin(self, plugin_name: str) -> str:
        """Deletes a plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            A string which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.delete_plugin(plugin_name="my_plugin_name")
        """
        return delete_plugin(self, plugin_name)

    @typechecked
    def update_plugin(
        self,
        plugin_path: Optional[str] = None,
        plugin_name: Optional[str] = None,
        verbose: bool = True,
        event_matcher: Optional[List[str]] = None,
        **kwargs,  # pylint: disable=missing-param-doc
    ) -> LiteralString:
        """Update a plugin with new code.

        Args:
            plugin_path: Path to your plugin. Either:

                - a folder containing a main.py (mandatory) and a requirements.txt (optional)
                - a .py file
            plugin_name: Name of the plugin
            event_matcher: List of events names and/or globs for which the plugin should be called.
            verbose: If false, minimal logs are displayed

        Returns:
            A string which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.update_plugin(plugin_name="my_plugin_name")
        """
        if kwargs.get("file_path"):
            raise TypeError(
                '"file_path" has been deprecated for "plugin_path", please use "plugin_path"'
                " instead"
            )

        if not plugin_path:
            raise TypeError('"plugin_path is nullish, please provide a value')

        if not plugin_name:
            raise TypeError('"plugin_name is nullish, please provide a value')

        return PluginUploader(
            self,  # pyright: ignore[reportGeneralTypeIssues]
            plugin_path,
            plugin_name,
            verbose,
            self.http_client,
            event_matcher,
        ).update_plugin()
