from .fragments import LABEL_FRAGMENT, LABEL_FRAGMENT_ID

GQL_CREATE_PREDICTIONS = f'''
mutation(
    $modelNameArray: [String!]!
    $jsonResponseArray: [String!]!
    $where: AssetWhere!
) {{
  data: createPredictions(
    modelNameArray: $modelNameArray
    jsonResponseArray: $jsonResponseArray
    where: $where
  ) {{
      {LABEL_FRAGMENT_ID}
  }}
}}
'''

GQL_APPEND_TO_LABELS = f'''
mutation(
    $authorID: ID!
    $jsonResponse: String!
    $labelType: LabelType!
    $secondsToLabel: Float
    $skipped: Boolean!
    $where: AssetWhere!
) {{
  data: appendToLabels(
    authorID: $authorID
    jsonResponse: $jsonResponse
    labelType: $labelType
    secondsToLabel: $secondsToLabel
    skipped: $skipped
    where: $where
  ) {{
      {LABEL_FRAGMENT_ID}
  }}
}}
'''


GQL_UPDATE_PROPERTIES_IN_LABEL = f'''
mutation(
    $labelID: ID!
    $secondsToLabel: Float
    $modelName: String
    $jsonResponse: String
) {{
  data: updatePropertiesInLabel(
    where: {{id: $labelID}}
    data: {{
      secondsToLabel: $secondsToLabel
      modelName: $modelName
      jsonResponse: $jsonResponse
    }}
  ) {{
    {LABEL_FRAGMENT_ID}
  }}
}}
'''

GQL_CREATE_HONEYPOT = f'''
mutation(
    $jsonResponse: String!
    $where: AssetWhere!
) {{
  data: createHoneypot(
    jsonResponse: $jsonResponse
    where: $where
  ) {{
      {LABEL_FRAGMENT}
  }}
}}
'''
