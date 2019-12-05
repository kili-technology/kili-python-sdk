from ..helper import format_result, json_escape


def update_tool(client, tool_id: str, project_id: str, name: str, tool_type: str, json_settings: str):
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
    ''' % (tool_id, project_id, name, tool_type, json_escape(json_settings)))
    return format_result('updateTool', result)


def append_to_tools(client, project_id: str, name: str, tool_type: str, json_settings: str):
    result = client.execute('''
    mutation {
      appendToTools(
        projectID: "%s",
        name: "%s",
        toolType: %s,
        jsonSettings: "%s") {
          id
      }
    }
    ''' % (project_id, name, tool_type, json_escape(json_settings)))
    return format_result('appendToTools', result)


def delete_from_tools(client, tool_id: str):
    result = client.execute('''
    mutation {
      deleteFromTools(toolID: "%s") {
        id
      }
    }
    ''' % (tool_id))
    return format_result('deleteFromTools', result)
