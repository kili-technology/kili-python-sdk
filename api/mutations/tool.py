from json import loads


def update_tool(client, tool_id, project_id, name, tool_type, json_settings):
    result = client.execute('''
    mutation {
      updateTool(toolID: "%s",
        projectID: "%s",
        name: "%s",
        toolType: %s,
        jsonSettings: "%s") {
          id
      }
    }
    ''' % (tool_id, project_id, name, tool_type, json_settings))
    return loads(result)['data']['updateTool']
