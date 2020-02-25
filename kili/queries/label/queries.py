from .fragments import LABEL_FRAGMENT

GQL_GET_LABEL = f'''
query ($assetID: ID!, $userID: ID!) {{
  data: getLabel(assetID: $assetID, userID: $userID) {{
    {LABEL_FRAGMENT}
  }}
}}
'''

GQL_GET_LATEST_LABELS_FOR_USER = f'''
query($projectID: ID!, $userID: ID!) {{
  data: getLatestLabelsForUser(projectID: $projectID, userID: $userID) {{
    {LABEL_FRAGMENT}
  }}
}}
'''

GQL_GET_LATEST_LABELS = f'''
query($projectID: ID!, $skip: Int!, $first: Int!) {{
  data: getLatestLabels(projectID: $projectID, skip: $skip, first: $first) {{
    {LABEL_FRAGMENT}
  }}
}}
'''
