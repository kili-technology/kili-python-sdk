"""
GraphQL Queries of Plugins
"""


from datetime import datetime
from typing import List, NamedTuple, Optional

from kili.graphql import GraphQLQuery, QueryOptions
from kili.helpers import format_result


class PluginLogsWhere(NamedTuple):
    """
    Tuple to be passed to the PluginQuery to restrict query
    """

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
        """
        Return the GraphQL list_plugins query
        """
        return f"""
        query listPlugins{{
            data: listPlugins {{
                {fragment}
            }}
        }}
        """

    def list(self, fields: List[str]):
        """
        List plugins
        """
        fragment = self.fragment_builder(fields)
        query = self.gql_list_plugins(fragment)
        result = self.client.execute(query)
        return format_result("data", result)

    def get_logs(self, where: PluginLogsWhere, options: QueryOptions):
        """
        Get logs of a plugin in Kili
        """

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
        return format_result("data", result)


GQL_GET_PLUGIN_RUNNER_STATUS = """
    query getPluginRunnerStatus(
        $name: String!
    ) {
        data: getPluginRunnerStatus(
            name: $name
        )
    }
    """
