from .fragments import TOOL_FRAGMENT

GQL_GET_TOOLS = f'''
query($projectID: ID!) {{
  data: getTools(projectID: $projectID) {{
    {TOOL_FRAGMENT}
  }}
}}
'''
