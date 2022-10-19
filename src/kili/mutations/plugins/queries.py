"""
Queries of plugins mutations
"""

GQL_UPLOAD_PLUGIN_BETA = """
mutation(
  $pluginName: String!
  $pluginSrc: String!
  ) {
  data: uploadPlugin(
    data: {
      pluginName: $pluginName
      pluginSrc: $pluginSrc
    }
  )
}
"""

GQL_ACTIVATE_PLUGIN_ON_PROJECT = """
mutation(
  $pluginName: String!
  $projectId: ID!
  ) {
  data: activatePluginOnProject(
    where: {
      pluginName: $pluginName
      projectId: $projectId
    }
  )
}
"""

GQL_DEACTIVATE_PLUGIN_ON_PROJECT = """
mutation(
  $pluginName: String!
  $projectId: ID!
  ) {
  data: deactivatePluginOnProject(
    where: {
      pluginName: $pluginName
      projectId: $projectId
    }
  )
}
"""
