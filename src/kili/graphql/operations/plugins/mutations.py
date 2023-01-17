"""
Plugins related mutations
"""

GQL_CREATE_PLUGIN = """
mutation(
  $pluginName: String!
  ) {
  data: createPlugin(
    data: {
      pluginName: $pluginName
    }
  )
}
"""

GQL_CREATE_PLUGIN_RUNNER = """
mutation(
  $pluginName: String!
  ) {
  data: createPluginRunner(
    data: {
      pluginName: $pluginName
    }
  )
}
"""

GQL_CREATE_WEBHOOK = """
mutation(
  $pluginName: String!
  $webhookUrl: String!
  $header: String
  ) {
  data: createWebhook(
    data: {
      header: $header
      pluginName: $pluginName
      webhookUrl: $webhookUrl
    }
  )
}
"""

GQL_GENERATE_UPDATE_URL = """
mutation(
  $pluginName: String!
  ) {
  data: generateUpdateUrl(
    data: {
      pluginName: $pluginName
    }
  )
}
"""

GQL_UPDATE_PLUGIN_RUNNER = """
mutation(
  $pluginName: String!
  ) {
  data: updatePluginRunner(
    data: {
      pluginName: $pluginName
    }
  )
}
"""

GQL_UPDATE_WEBHOOK = """
mutation(
  $pluginName: String!
  $webhookUrl: String!
  $header: String
  ) {
  data: updateWebhook(
    data: {
      header: $header
      pluginName: $pluginName
      webhookUrl: $webhookUrl
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

GQL_DELETE_PLUGIN = """
mutation(
  $pluginName: String!
  ) {
  data: deletePlugin(
    where: {
      pluginName: $pluginName
    }
  )
}
"""
