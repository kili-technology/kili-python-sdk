from .fragments import LABEL_HISTORY_FRAGMENT

GQL_APPEND_TO_LABEL_HISTORY = f'''
mutation(
    $assetID: ID!
    $authorID: ID!
    $inputType: InputType!
    $jsonInterface: String!
    $jsonResponse: String!
) {{
  data: appendToLabelHistory(
    assetID: $assetID,
    authorID: $authorID
    inputType: $inputType
    jsonInterface: $jsonInterface
    jsonResponse: $jsonResponse
  ) {{
    {LABEL_HISTORY_FRAGMENT}
  }}
}}
'''
