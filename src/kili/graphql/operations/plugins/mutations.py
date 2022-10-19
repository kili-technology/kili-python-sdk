"""
Plugins related mutations
"""

GQL_UPLOAD_PLUGIN_BETA = """
mutation(
  $pluginSrc: String!
  $pluginName: String!
  ) {
  data: uploadPlugin(
    data: {
      pluginSrc: $pluginSrc
      pluginName: $pluginName
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
