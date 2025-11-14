"""Plugins domain namespace for the Kili Python SDK."""

from datetime import datetime
from typing import Dict, List, Optional

from typeguard import typechecked
from typing_extensions import LiteralString, deprecated

from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.domain_api.namespace_utils import get_available_methods


class WebhooksNamespace:
    """Webhooks nested namespace for plugin webhook operations.

    This namespace provides access to webhook-related functionality
    within the plugins domain, including creating and updating webhooks.
    """

    def __init__(self, client):
        """Initialize the webhooks namespace.

        Args:
            client: The Kili client instance
        """
        self._client = client

    @deprecated(
        "'plugins.webhooks' is a namespace, not a callable method. "
        "Use kili.plugins.webhooks.create() or other available methods instead."
    )
    def __call__(self, *args, **kwargs):
        """Raise a helpful error when namespace is called like a method.

        This provides guidance to users migrating from the legacy API.
        """
        available_methods = get_available_methods(self)
        methods_str = ", ".join(f"kili.plugins.webhooks.{m}()" for m in available_methods)
        raise TypeError(
            f"'plugins.webhooks' is a namespace, not a callable method. "
            f"The domain API provides methods for webhook operations.\n"
            f"Available methods: {methods_str}\n"
            f"Example: kili.plugins.webhooks.create(webhook_url='...', plugin_name='...')"
        )

    @typechecked
    def create(
        self,
        webhook_url: str,
        plugin_name: str,
        header: Optional[str] = None,
        verbose: bool = True,
        handler_type: Optional[str] = None,
        handler_types: Optional[List[str]] = None,
        event_pattern: Optional[str] = None,
        event_matcher: Optional[List[str]] = None,
    ) -> str:
        """Create a webhook linked to Kili's events.

        For a complete example, refer to the notebook `webhooks_example` on kili repo.

        Args:
            webhook_url: URL receiving post requests on events on Kili. The payload will be:
                - eventType: the type of event called
                - logPayload:
                    - runId: a unique identifier of the run for observability
                    - projectId: the Kili project the webhook is called on
                - payload: the event produced, for example for `onSubmit` event:
                    - label: the label produced
                    - asset_id: the asset on which the label is produced
            plugin_name: Name of your plugin
            header: Authorization header to access the routes
            verbose: If false, minimal logs are displayed
            handler_type: Action for which the webhook should be called.
                Possible variants: `onSubmit`, `onReview`.
            handler_types: List of actions for which the webhook should be called.
                Possible variants: `onSubmit`, `onReview`.
                By default, is [`onSubmit`, `onReview`].
            event_pattern: Event pattern for which the webhook should be called.
            event_matcher: List of events for which the webhook should be called.

        Returns:
            A string which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> # Create a simple webhook
            >>> result = kili.plugins.webhooks.create(
            ...     webhook_url='https://my-custom-url-publicly-accessible/',
            ...     plugin_name='my webhook',
            ...     header='Bearer token123'
            ... )

            >>> # Create webhook with single handler type
            >>> result = kili.plugins.webhooks.create(
            ...     webhook_url='https://my-webhook.com/api/kili',
            ...     plugin_name='custom webhook',
            ...     handler_type='onSubmit',
            ...     event_pattern='project.*'
            ... )

            >>> # Create webhook with multiple handler types
            >>> result = kili.plugins.webhooks.create(
            ...     webhook_url='https://my-webhook.com/api/kili',
            ...     plugin_name='custom webhook',
            ...     handler_types=['onSubmit', 'onReview'],
            ...     event_matcher=['project.*', 'asset.*']
            ... )
        """
        # Convert singular to plural
        if handler_type is not None:
            handler_types = [handler_type]
        if event_pattern is not None:
            event_matcher = [event_pattern]

        return self._client.create_webhook(
            webhook_url, plugin_name, header, verbose, handler_types, event_matcher
        )

    @typechecked
    def update(
        self,
        new_webhook_url: str,
        plugin_name: str,
        new_header: Optional[str] = None,
        verbose: bool = True,
        handler_type: Optional[str] = None,
        handler_types: Optional[List[str]] = None,
        event_pattern: Optional[str] = None,
        event_matcher: Optional[List[str]] = None,
    ) -> str:
        """Update a webhook linked to Kili's events.

        For a complete example, refer to the notebook `webhooks_example` on kili repo.

        Args:
            new_webhook_url: New URL receiving post requests on events on Kili.
                See `create` for the payload description
            plugin_name: Name of your plugin
            new_header: Authorization header to access the routes
            verbose: If false, minimal logs are displayed
            handler_type: Action for which the webhook should be called.
                Possible variants: `onSubmit`, `onReview`.
            handler_types: List of actions for which the webhook should be called.
                Possible variants: `onSubmit`, `onReview`.
                By default, is [`onSubmit`, `onReview`]
            event_pattern: Event pattern for which the webhook should be called.
            event_matcher: List of events for which the webhook should be called.

        Returns:
            A string which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> # Update webhook URL and header
            >>> result = kili.plugins.webhooks.update(
            ...     new_webhook_url='https://new-webhook.com/api/kili',
            ...     plugin_name='my webhook',
            ...     new_header='Bearer new_token456'
            ... )

            >>> # Update webhook with single handler
            >>> result = kili.plugins.webhooks.update(
            ...     new_webhook_url='https://updated-webhook.com/api',
            ...     plugin_name='my webhook',
            ...     handler_type='onSubmit',
            ...     event_pattern='asset.*'
            ... )

            >>> # Update webhook with multiple event handlers
            >>> result = kili.plugins.webhooks.update(
            ...     new_webhook_url='https://updated-webhook.com/api',
            ...     plugin_name='my webhook',
            ...     handler_types=['onSubmit', 'onReview'],
            ...     event_matcher=['asset.*', 'label.*']
            ... )
        """
        # Convert singular to plural
        if handler_type is not None:
            handler_types = [handler_type]
        if event_pattern is not None:
            event_matcher = [event_pattern]

        return self._client.update_webhook(
            new_webhook_url, plugin_name, new_header, verbose, handler_types, event_matcher
        )


class PluginsNamespace(DomainNamespace):
    """Plugins domain namespace providing plugin-related operations.

    This namespace provides access to all plugin-related functionality
    including creating, updating, querying, managing plugins and their webhooks.

    The namespace provides the following main operations:
    - list(): Query and list plugins in the organization
    - status(): Get the status of a specific plugin
    - logs(): Get logs for a plugin on a project
    - build_errors(): Get build errors for a plugin
    - activate(): Activate a plugin on a project
    - deactivate(): Deactivate a plugin from a project
    - create(): Create/upload a new plugin
    - update(): Update an existing plugin with new code
    - delete(): Delete a plugin from the organization
    - webhooks: Nested namespace for webhook operations (create, update)

    Examples:
        >>> kili = Kili()
        >>> # List all plugins
        >>> plugins = kili.plugins.list()

        >>> # Get plugin status
        >>> status = kili.plugins.status(plugin_name="my_plugin")

        >>> # Get plugin logs
        >>> logs = kili.plugins.logs(
        ...     project_id="project_123",
        ...     plugin_name="my_plugin"
        ... )

        >>> # Create a new plugin
        >>> result = kili.plugins.create(
        ...     plugin_path="./my_plugin/",
        ...     plugin_name="my_plugin"
        ... )

        >>> # Activate plugin on project
        >>> kili.plugins.activate(
        ...     plugin_name="my_plugin",
        ...     project_id="project_123"
        ... )

        >>> # Create a webhook
        >>> kili.plugins.webhooks.create(
        ...     webhook_url="https://my-webhook.com/api",
        ...     plugin_name="my_webhook"
        ... )
    """

    def __init__(self, client, gateway):
        """Initialize the plugins namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations
        """
        super().__init__(client, gateway, "plugins")
        self._webhooks_namespace = WebhooksNamespace(self._client)

    @deprecated(
        "'plugins' is a namespace, not a callable method. "
        "Use kili.plugins.list() or other available methods instead."
    )
    def __call__(self, *args, **kwargs):
        """Raise a helpful error when namespace is called like a method.

        This provides guidance to users migrating from the legacy API
        where plugins were accessed via kili.plugins(...) to the new domain API
        where they use kili.plugins.list(...) or other methods.
        """
        available_methods = get_available_methods(self)
        methods_str = ", ".join(f"kili.{self._domain_name}.{m}()" for m in available_methods)
        raise TypeError(
            f"'{self._domain_name}' is a namespace, not a callable method. "
            f"The legacy API 'kili.{self._domain_name}(...)' has been replaced with the domain API.\n"
            f"Available methods: {methods_str}\n"
            f"Nested namespaces: kili.{self._domain_name}.webhooks\n"
            f"Example: kili.{self._domain_name}.list(...)"
        )

    @property
    def webhooks(self) -> WebhooksNamespace:
        """Get the webhooks nested namespace for webhook operations.

        Returns:
            The WebhooksNamespace instance for webhook-specific operations.
        """
        return self._webhooks_namespace

    @typechecked
    def list(
        self,
        fields: ListOrTuple[str] = ("name", "projectIds", "id", "createdAt", "updatedAt"),
    ) -> List[Dict]:
        """List all plugins from your organization.

        Args:
            fields: All the fields to request among the possible fields for the plugins.
                See [the documentation](https://api-docs.kili-technology.com/types/objects/plugin)
                for all possible fields.

        Returns:
            A list of plugin dictionaries containing the requested fields.

        Examples:
            >>> # Get all plugins with default fields
            >>> plugins = kili.plugins.list()

            >>> # Get specific fields only
            >>> plugins = kili.plugins.list(fields=['name', 'id'])

            >>> # Get all available fields
            >>> plugins = kili.plugins.list(fields=[
            ...     'id', 'name', 'projectIds', 'createdAt', 'updatedAt',
            ...     'organizationId', 'archived'
            ... ])
        """
        return self._client.list_plugins(fields)

    @typechecked
    def status(
        self,
        plugin_name: str,
        verbose: bool = True,
    ) -> str:
        """Get the status of a plugin.

        Args:
            plugin_name: Name of the plugin
            verbose: If false, minimal logs are displayed

        Returns:
            The status of the plugin if query was successful or an error message otherwise.

        Examples:
            >>> # Get plugin status
            >>> status = kili.plugins.status(plugin_name="my_plugin_name")

            >>> # Get status with minimal logging
            >>> status = kili.plugins.status(
            ...     plugin_name="my_plugin_name",
            ...     verbose=False
            ... )
        """
        return self._client.get_plugin_status(plugin_name, verbose)

    @typechecked
    def logs(
        self,
        project_id: str,
        plugin_name: str,
        start_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> str:
        """Get paginated logs of a plugin on a project.

        Args:
            project_id: Identifier of the project
            plugin_name: Name of the plugin
            start_date: Datetime used to get the logs from, if not provided,
                it will be the plugin's creation date
            limit: Limit for pagination, if not provided, it will be 100
            skip: Skip for pagination, if not provided, it will be 0

        Returns:
            A JSON string containing the logs of the plugin, or an error message.

        Examples:
            >>> # Get recent logs
            >>> logs = kili.plugins.logs(
            ...     project_id="my_project_id",
            ...     plugin_name="my_plugin_name"
            ... )

            >>> # Get logs from a specific date
            >>> from datetime import datetime
            >>> logs = kili.plugins.logs(
            ...     project_id="my_project_id",
            ...     plugin_name="my_plugin_name",
            ...     start_date=datetime(2023, 1, 1)
            ... )

            >>> # Get logs with pagination
            >>> logs = kili.plugins.logs(
            ...     project_id="my_project_id",
            ...     plugin_name="my_plugin_name",
            ...     limit=50,
            ...     skip=100
            ... )
        """
        return self._client.get_plugin_logs(project_id, plugin_name, start_date, limit, skip)

    @typechecked
    def build_errors(
        self,
        plugin_name: str,
        start_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> str:
        """Get paginated build errors of a plugin.

        Args:
            plugin_name: Name of the plugin
            start_date: Datetime used to get the build errors from, if not provided,
                it will be the plugin's creation date
            limit: Limit for pagination, if not provided, it will be 100
            skip: Skip for pagination, if not provided, it will be 0

        Returns:
            A JSON string containing the build errors of the plugin, or an error message.

        Examples:
            >>> # Get recent build errors
            >>> errors = kili.plugins.build_errors(plugin_name="my_plugin_name")

            >>> # Get build errors from a specific date
            >>> from datetime import datetime
            >>> errors = kili.plugins.build_errors(
            ...     plugin_name="my_plugin_name",
            ...     start_date=datetime(2023, 1, 1)
            ... )

            >>> # Get build errors with pagination
            >>> errors = kili.plugins.build_errors(
            ...     plugin_name="my_plugin_name",
            ...     limit=50,
            ...     skip=0
            ... )
        """
        return self._client.get_plugin_build_errors(plugin_name, start_date, limit, skip)

    @typechecked
    def activate(self, plugin_name: str, project_id: str) -> Optional[str]:
        """Activate a plugin on a project.

        Args:
            plugin_name: Name of the plugin
            project_id: Identifier of the project

        Returns:
            A string which indicates if the operation was successful, or an error message.

        Examples:
            >>> # Activate plugin on project
            >>> result = kili.plugins.activate(
            ...     plugin_name="my_plugin_name",
            ...     project_id="my_project_id"
            ... )
        """
        return self._client.activate_plugin_on_project(plugin_name, project_id)

    @typechecked
    def deactivate(self, plugin_name: str, project_id: str) -> str:
        """Deactivate a plugin on a project.

        Args:
            plugin_name: Name of the plugin
            project_id: Identifier of the project

        Returns:
            A string which indicates if the operation was successful, or an error message.

        Examples:
            >>> # Deactivate plugin from project
            >>> result = kili.plugins.deactivate(
            ...     plugin_name="my_plugin_name",
            ...     project_id="my_project_id"
            ... )
        """
        return self._client.deactivate_plugin_on_project(plugin_name, project_id)

    @typechecked
    def create(
        self,
        plugin_path: str,
        plugin_name: Optional[str] = None,
        verbose: bool = True,
        event_pattern: Optional[str] = None,
        event_matcher: Optional[List[str]] = None,
    ) -> LiteralString:
        """Create and upload a new plugin.

        Args:
            plugin_path: Path to your plugin. Either:
                - a folder containing a main.py (mandatory) and a requirements.txt (optional)
                - a .py file
            plugin_name: Name of your plugin, if not provided, it will be the name from your file
            event_pattern: Event pattern for which the plugin should be called.
            event_matcher: List of events for which the plugin should be called.
            verbose: If false, minimal logs are displayed

        Returns:
            A string which indicates if the operation was successful, or an error message.

        Examples:
            >>> # Upload a plugin from a folder
            >>> result = kili.plugins.create(plugin_path="./path/to/my/folder")

            >>> # Upload a plugin from a single file
            >>> result = kili.plugins.create(plugin_path="./path/to/my/file.py")

            >>> # Upload with custom name and single event pattern
            >>> result = kili.plugins.create(
            ...     plugin_path="./my_plugin/",
            ...     plugin_name="custom_plugin_name",
            ...     event_pattern="onSubmit"
            ... )

            >>> # Upload with custom name and multiple event matchers
            >>> result = kili.plugins.create(
            ...     plugin_path="./my_plugin/",
            ...     plugin_name="custom_plugin_name",
            ...     event_matcher=["onSubmit", "onReview"]
            ... )
        """
        # Convert singular to plural
        if event_pattern is not None:
            event_matcher = [event_pattern]

        return self._client.upload_plugin(plugin_path, plugin_name, verbose, event_matcher)

    @typechecked
    def update(
        self,
        plugin_path: str,
        plugin_name: str,
        verbose: bool = True,
        event_pattern: Optional[str] = None,
        event_matcher: Optional[List[str]] = None,
    ) -> LiteralString:
        """Update a plugin with new code.

        Args:
            plugin_path: Path to your plugin. Either:
                - a folder containing a main.py (mandatory) and a requirements.txt (optional)
                - a .py file
            plugin_name: Name of the plugin to update
            event_pattern: Event pattern for which the plugin should be called.
            event_matcher: List of events names and/or globs for which the plugin should be called.
            verbose: If false, minimal logs are displayed

        Returns:
            A string which indicates if the operation was successful, or an error message.

        Examples:
            >>> # Update plugin with new code
            >>> result = kili.plugins.update(
            ...     plugin_path="./updated_plugin/",
            ...     plugin_name="my_plugin_name"
            ... )

            >>> # Update plugin with single event pattern
            >>> result = kili.plugins.update(
            ...     plugin_path="./updated_plugin.py",
            ...     plugin_name="my_plugin_name",
            ...     event_pattern="project.*"
            ... )

            >>> # Update plugin with multiple event matchers
            >>> result = kili.plugins.update(
            ...     plugin_path="./updated_plugin.py",
            ...     plugin_name="my_plugin_name",
            ...     event_matcher=["project.*", "asset.*"]
            ... )
        """
        # Convert singular to plural
        if event_pattern is not None:
            event_matcher = [event_pattern]

        return self._client.update_plugin(plugin_path, plugin_name, verbose, event_matcher)

    @typechecked
    def delete(self, plugin_name: str) -> str:
        """Delete a plugin from the organization.

        Args:
            plugin_name: Name of the plugin to delete

        Returns:
            A string which indicates if the operation was successful, or an error message.

        Examples:
            >>> # Delete a plugin
            >>> result = kili.plugins.delete(plugin_name="my_plugin_name")
        """
        return self._client.delete_plugin(plugin_name)
