from json import dumps

from ...helpers import format_result
from .queries import (GQL_APPEND_TO_TOOLS, GQL_DELETE_FROM_TOOLS,
                      GQL_UPDATE_TOOL)


def update_tool(client, tool_id: str, project_id: str, json_settings: dict):
    variables = {
        'toolID': tool_id,
        'projectID': project_id,
        'jsonSettings': dumps(json_settings)
    }
    result = client.execute(GQL_UPDATE_TOOL, variables)
    return format_result('data', result)


def append_to_tools(client, project_id: str,  json_settings: dict):
    variables = {
        'projectID': project_id,
        'jsonSettings': dumps(json_settings)
    }
    result = client.execute(GQL_APPEND_TO_TOOLS, variables)
    return format_result('data', result)


def delete_from_tools(client, tool_id: str):
    variables = {'toolID': tool_id}
    result = client.execute(GQL_DELETE_FROM_TOOLS, variables)
    return format_result('data', result)
