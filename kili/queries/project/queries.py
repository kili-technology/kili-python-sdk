from .fragments import PROJECT_FRAGMENT

GQL_GET_PROJECTS = f'''
query($userID: ID!) {{
  data: getProjects(userID: $userID) {{
    {PROJECT_FRAGMENT}
  }}
}}
'''

GQL_GET_PROJECT = f'''
query($projectID: ID!) {{
  data: getProject(projectID: $projectID) {{
    {PROJECT_FRAGMENT}
  }}
}}
'''
