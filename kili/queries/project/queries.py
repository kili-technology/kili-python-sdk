from .fragments import PROJECT_FRAGMENT

GQL_GET_PROJECTS = f'''
query($userID: ID!, $searchQuery: String, $skip: Int!, $first: Int!) {{
  data: getProjects(userID: $userID, searchQuery: $searchQuery, skip: $skip, first: $first) {{
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
