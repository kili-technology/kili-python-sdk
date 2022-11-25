"""
Plugins related queries
"""

from kili.graphql.operations.plugins.fragments import PLUGIN_LOG_FRAGMENT

GQL_GET_PLUGIN_LOGS = f"""
query(
    $projectId: ID!
    $pluginName: String!
    $createdAt: DateTime
    $limit: Int
    $skip: Int
  ) {{
  data: getPluginLogs(
    data: {{
      projectId: $projectId
      pluginName: $pluginName
      createdAt: $createdAt
      limit: $limit
      skip: $skip
    }}
  ) {{
    {PLUGIN_LOG_FRAGMENT}
  }}
}}
"""

GQL_GET_PLUGIN_RUNNER_STATUS = """
query(
  $name: String!
  ) {
  data: getPluginRunnerStatus(
    name: $name
  )
}
"""


def gql_list_plugins(fragment):
    """
    Return the GraphQL list_plugins query
    """
    return f"""
query {{
  data: listPlugins {{
    {fragment}
  }}
}}
"""
