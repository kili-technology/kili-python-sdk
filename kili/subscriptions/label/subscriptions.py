from .fragments import LABEL_FRAGMENT

GQL_LABEL_CREATED_OR_UPDATED = f'''
subscription($projectID: ID!) {{
  data: labelCreatedOrUpdated(projectID: $projectID) {{
    {LABEL_FRAGMENT}
  }}
}}
'''
