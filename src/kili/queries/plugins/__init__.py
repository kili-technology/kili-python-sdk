"""Plugins queries."""

import json
from datetime import datetime
from typing import Optional

from typeguard import typechecked

from kili.services.plugins import PluginUploader, get_logs


class QueriesPlugins:
    """Set of Plugins queries."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @typechecked
    def get_plugin_logs(
        self,
        project_id: str,
        plugin_name: str,
        start_date: Optional[datetime] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
    ):
        # pylint: disable=line-too-long
        """Get paginated logs of a plugin on a project.
        Args:
            project_id: Identifier of the project
            plugin_name: Name of the plugin
            start_date: Datetime used to get the logs from, if not provided, it will be the plugin's creation date
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
        return json.dumps(pretty_result, sort_keys=True, indent=4)

    @typechecked
    def get_plugin_status(
        self,
        plugin_name: str,
        verbose: bool = True,
    ):
        """Update a plugin with new code.

        Args:
            plugin_name: Name of the plugin
            verbose: If false, minimal logs are displayed

        Returns:
            The status of the plugin if query was successful or an error message otherwise.

        Examples:
            >>> kili.get_plugin_status(plugin_name="my_plugin_name")
        """

        result = PluginUploader(self.auth, "", plugin_name, verbose).get_plugin_runner_status()
        return result
