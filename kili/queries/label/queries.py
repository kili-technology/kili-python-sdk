from .fragments import LABEL_FRAGMENT

GQL_LABELS = f'''
query (
  $assetID: ID
  $labelID: ID 
  $projectID: ID 
  $userID: ID
  $skip: Int!
  $first: PageSize!) {{
  data: labels(
    where: {{
      id: $labelID
      asset: {{ id: $assetID }}
      project: {{ id: $projectID }} 
      user: {{ id: $userID }} 
    }}
    skip: $skip
    first: $first
    ) {{
    {LABEL_FRAGMENT}
  }}
}}
'''
