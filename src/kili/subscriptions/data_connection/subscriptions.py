"""
Subscriptions for data connection
"""

from .fragments import DATA_CONNECTION_FRAGMENT

GQL_DATA_CONNECTION_UPDATED_SUBSCRIPTION = f"""
subscription dataConnectionUpdated($projectID: ID!) {{
  data: dataConnectionUpdated(projectID: $projectID) {{
    {DATA_CONNECTION_FRAGMENT}
  }}
}}
"""
