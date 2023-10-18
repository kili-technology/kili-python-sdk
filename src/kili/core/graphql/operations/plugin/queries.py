"""GraphQL Queries of Plugins."""

from datetime import datetime
from typing import NamedTuple, Optional

from kili.adapters.kili_api_gateway.helpers.queries import fragment_builder
from kili.core.graphql.queries import GraphQLQuery, QueryOptions
from kili.domain.types import ListOrTuple


class PluginBuildErrorsWhere(NamedTuple):
    """Tuple to be passed to the PluginQuery to restrict query."""

    plugin_name: str
    start_date: Optional[datetime]


class PluginLogsWhere(NamedTuple):
    """Tuple to be passed to the PluginQuery to restrict query."""

    project_id: str
    plugin_name: str
    start_date: Optional[datetime]


class PluginQuery(GraphQLQuery):
    """Plugin query."""

    @staticmethod
    def query(fragment):
        """The Plugin query is not implemented as other queries.

        To overpass the technical debt, the plugin query is access by calling the list method
        """
        _ = fragment
        return NotImplemented

    COUNT_QUERY = """
    query countPlugins($where: PluginWhere!) {
        data: countPlugins(where: $where)
    }
    """

    GQL_GET_PLUGIN_BUILD_ERRORS = """
    query getPluginBuildErrors(
        $pluginName: String!
        $createdAt: DateTime
        $limit: Int
        $skip: Int
    ) {
        data: getPluginBuildErrors(
            data: {
                pluginName: $pluginName
                createdAt: $createdAt
                limit: $limit
                skip: $skip
            }
        ) {
            content
            createdAt
            logType
            pluginName
        }
    }
    """

    GQL_GET_PLUGIN_LOGS = """
    query getPluginLogs(
        $projectId: ID!
        $pluginName: String!
        $createdAt: DateTime
        $limit: Int
        $skip: Int
    ) {
        data: getPluginLogs(
            data: {
                projectId: $projectId
                pluginName: $pluginName
                createdAt: $createdAt
                limit: $limit
                skip: $skip
            }
        ) {
            content
            createdAt
            logType
            metadata {
                assetId
                labelId
            }
            pluginName
            projectId
            runId
        }
    }
    """

    @staticmethod
    def gql_list_plugins(fragment):
        """Return the GraphQL list_plugins query."""
        return f"""
        query listPlugins{{
            data: listPlugins {{
                {fragment}
            }}
        }}
        """

    def list(self, fields: ListOrTuple[str]):
        """List plugins."""
        fragment = fragment_builder(fields)
        query = self.gql_list_plugins(fragment)
        result = self.client.execute(query)
        return self.format_result("data", result)

    def get_build_errors(self, where: PluginBuildErrorsWhere, options: QueryOptions):
        """Get build errors of a plugin in Kili."""
        payload = {
            "pluginName": where.plugin_name,
            "limit": options.first,
            "skip": options.skip,
        }

        if where.start_date:
            payload["createdAt"] = (
                where.start_date.isoformat(sep="T", timespec="milliseconds") + "Z"
            )

        result = self.client.execute(self.GQL_GET_PLUGIN_BUILD_ERRORS, payload)
        return self.format_result("data", result)

    def get_logs(self, where: PluginLogsWhere, options: QueryOptions):
        """Get logs of a plugin in Kili."""
        payload = {
            "projectId": where.project_id,
            "pluginName": where.plugin_name,
            "limit": options.first,
            "skip": options.skip,
        }

        if where.start_date:
            payload["createdAt"] = (
                where.start_date.isoformat(sep="T", timespec="milliseconds") + "Z"
            )

        result = self.client.execute(self.GQL_GET_PLUGIN_LOGS, payload)
        return self.format_result("data", result)


GQL_GET_PLUGIN_RUNNER_STATUS = """
    query getPluginRunnerStatus(
        $name: String!
    ) {
        data: getPluginRunnerStatus(
            name: $name
        )
    }
    """
