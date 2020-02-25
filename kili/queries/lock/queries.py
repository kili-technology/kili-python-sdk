from .fragments import LOCK_FRAGMENT

GQL_GET_LOCKS = f'''
query($projectID: ID!) {{
  data: getLocks(projectID: $projectID) {{
    {LOCK_FRAGMENT}
  }}
}}
'''
