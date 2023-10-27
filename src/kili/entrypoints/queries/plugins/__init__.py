"""Plugins queries."""

import json
from datetime import datetime
from typing import Dict, List, Optional

from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.core.graphql.operations.plugin.queries import (
    PluginBuildErrorsWhere,
    PluginLogsWhere,
    PluginQuery,
)
from kili.domain.types import ListOrTuple
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.services.plugins import PluginUploader
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class QueriesPlugins(BaseOperationEntrypointMixin):
    """Set of Plugins queries."""

    # pylint: disable=too-many-arguments

    @typechecked
    def get_plugin_build_errors(
        self,
        plugin_name: str,
        start_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> str:
        # pylint: disable=line-too-long
        """Get paginated build errors of a plugin.

        Args:
            plugin_name: Name of the plugin
            start_date: Datetime used to get the build errors from, if not provided, it will be the plugin's creation date
            limit: Limit for pagination, if not provided, it will be 100
            skip: Skip for pagination, if not provided, it will be 0
        Returns:
            A result array which contains the build errors of the plugin,
                or an error message.

        Examples:
            >>> kili.get_plugin_build_errors(plugin_name="my_plugin_name", start_date="1970/01/01")
        """
        where = PluginBuildErrorsWhere(plugin_name=plugin_name, start_date=start_date)
        options = QueryOptions(
            first=limit, skip=skip, disable_tqdm=False
        )  # disable tqm is not implemented for this query
        pretty_result = PluginQuery(self.graphql_client, self.http_client).get_build_errors(
            where, options
        )
        return json.dumps(pretty_result, sort_keys=True, indent=4)

    @typechecked
    def get_plugin_logs(
        self,
        project_id: str,
        plugin_name: str,
        start_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> str:
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
        where = PluginLogsWhere(
            project_id=project_id, plugin_name=plugin_name, start_date=start_date
        )
        options = QueryOptions(
            first=limit, skip=skip, disable_tqdm=False
        )  # disable tqm is not implemented for this query
        pretty_result = PluginQuery(self.graphql_client, self.http_client).get_logs(where, options)
        return json.dumps(pretty_result, sort_keys=True, indent=4)

    @typechecked
    def get_plugin_status(
        self,
        plugin_name: str,
        verbose: bool = True,
    ) -> str:
        """Update a plugin with new code.

        Args:
            plugin_name: Name of the plugin
            verbose: If false, minimal logs are displayed

        Returns:
            The status of the plugin if query was successful or an error message otherwise.

        Examples:
            >>> kili.get_plugin_status(plugin_name="my_plugin_name")
        """
        return PluginUploader(
            self,  # pyright: ignore[reportGeneralTypeIssues]
            "",
            plugin_name,
            verbose,
            self.http_client,
        ).get_plugin_runner_status()

    @typechecked
    def list_plugins(
        self,
        fields: ListOrTuple[str] = ("name", "projectIds", "id", "createdAt", "updatedAt"),
    ) -> List[Dict]:
        # pylint: disable=line-too-long
        """List all plugins from your organization.

        Args:
            fields: All the fields to request among the possible fields for the plugins
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#plugins) for all possible fields.

        Returns:
            A result array which contains all the plugins from your organization,
                or an error message.

        Examples:
            >>> kili.list_plugins()
            >>> kili.list_plugins(fields=['name'])
        """
        return PluginQuery(self.graphql_client, self.http_client).list(fields=fields)
