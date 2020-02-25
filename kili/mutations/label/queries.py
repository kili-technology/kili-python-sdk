from .fragments import LABEL_FRAGMENT, LABEL_FRAGMENT_ID

GQL_CREATE_PREDICTIONS = f'''
mutation(
    $projectID: ID!
    $externalIDArray: [ID!]!
    $modelNameArray: [String!]!
    $jsonResponseArray: [String!]!
) {{
  data: createPredictions(
    projectID: $projectID
    externalIDArray: $externalIDArray
    modelNameArray: $modelNameArray
    jsonResponseArray: $jsonResponseArray) {{
      {LABEL_FRAGMENT_ID}
  }}
}}
'''

GQL_APPEND_TO_LABELS = f'''
mutation(
    $authorID: ID!
    $jsonResponse: String!
    $labelAssetID: ID!
    $labelType: LabelType!
    $secondsToLabel: Float
    $skipped: Boolean!
) {{
  data: appendToLabels(
    authorID: $authorID
    jsonResponse: $jsonResponse
    labelAssetID: $labelAssetID
    labelType: $labelType
    secondsToLabel: $secondsToLabel
    skipped: $skipped) {{
      {LABEL_FRAGMENT_ID}
  }}
}}
'''

GQL_UPDATE_LABEL = f'''
mutation(
    $labelID: ID!
    $labelAssetID: ID
    $reviewAssetID: ID
    $authorID: ID!
    $labelType: LabelType!
    $jsonResponse: String!
    $secondsToLabel: Float
) {{
  data: updateLabel(
    labelID: $labelID
    labelAssetID: $labelAssetID
    reviewAssetID: $reviewAssetID
    authorID: $authorID
    labelType: $labelType
    jsonResponse: $jsonResponse
    secondsToLabel: $secondsToLabel) {{
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
    $assetID: ID!
    $jsonResponse: String!
) {{
  data: createHoneypot(
    assetID: $assetID
    jsonResponse: $jsonResponse) {{
      {LABEL_FRAGMENT}
  }}
}}
'''
