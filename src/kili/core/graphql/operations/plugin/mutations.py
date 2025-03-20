"""Plugins related mutations."""

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
  $eventMatcher: [String!]
  $handlerTypes: [PluginHandlerType!]
  $pluginName: String!
  ) {
  data: createPluginRunner(
    data: {
      eventMatcher: $eventMatcher
      handlerTypes: $handlerTypes
      pluginName: $pluginName
    }
  )
}
"""

GQL_CREATE_WEBHOOK = """
mutation(
  $eventMatcher: [String!]
  $handlerTypes: [PluginHandlerType!]
  $pluginName: String!
  $webhookUrl: String!
  $header: String
  ) {
  data: createWebhook(
    data: {
      eventMatcher: $eventMatcher
      handlerTypes: $handlerTypes
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
  $eventMatcher: [String!]
  $handlerTypes: [PluginHandlerType!]
  $pluginName: String!
  ) {
  data: updatePluginRunner(
    data: {
      eventMatcher: $eventMatcher
      handlerTypes: $handlerTypes
      pluginName: $pluginName
    }
  )
}
"""

GQL_UPDATE_WEBHOOK = """
mutation(
  $eventMatcher: [String!]
  $handlerTypes: [PluginHandlerType!]
  $pluginName: String!
  $webhookUrl: String!
  $header: String
  ) {
  data: updateWebhook(
    data: {
      eventMatcher: $eventMatcher
      handlerTypes: $handlerTypes
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
