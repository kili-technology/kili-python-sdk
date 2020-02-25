from .fragments import TOOL_FRAGMENT

GQL_UPDATE_TOOL = f'''
mutation($toolID: ID!, $projectID: ID!, $jsonSettings: String!) {{
  data: updateTool(toolID: $toolID
    projectID: $projectID
    jsonSettings: $jsonSettings) {{
      {TOOL_FRAGMENT}
  }}
}}
'''

GQL_APPEND_TO_TOOLS = f'''
mutation($projectID: ID!, $jsonSettings: String!) {{
  data: appendToTools(
    projectID: $projectID
    jsonSettings: $jsonSettings) {{
      {TOOL_FRAGMENT}
  }}
}}
'''

GQL_DELETE_FROM_TOOLS = f'''
mutation($toolID: ID!) {{
  data: deleteFromTools(toolID: $toolID) {{
    {TOOL_FRAGMENT}
  }}
}}
'''
