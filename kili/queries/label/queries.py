from .fragments import LABEL_FRAGMENT

GQL_LABELS = f'''
query (
  $assetID: ID 
  $userID: ID
  $skip: Int!
  $first: PageSize!) {{
  data: labels(
    where: {{ 
      asset: {{ id: $assetID }}, 
      user: {{ id: $userID }} 
    }}
    skip: $skip
    first: $first
    ) {{
    {LABEL_FRAGMENT}
  }}
}}
'''
