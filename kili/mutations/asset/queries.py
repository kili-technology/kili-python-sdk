from .fragments import ASSET_FRAGMENT


GQL_APPEND_MANY_TO_DATASET = f'''
mutation(
    $projectID: ID!,
    $contentArray: [String!],
    $externalIDArray: [String!],
    $isHoneypotArray: [Boolean!],
    $statusArray: [Status!],
    $jsonMetadataArray: [String!]) {{
  data: appendManyToDataset(
    projectID: $projectID,
    contentArray: $contentArray,
    externalIDArray: $externalIDArray,
    isHoneypotArray: $isHoneypotArray,
    statusArray: $statusArray,
    jsonMetadataArray: $jsonMetadataArray
  ) {{
    {ASSET_FRAGMENT}
  }}
}}
'''


GQL_UPDATE_PROPERTIES_IN_ASSET = f'''
mutation(
    $assetID: ID!
    $consensusMark: Float
    $content: String
    $externalId: String
    $honeypotMark: Float
    $isHoneypot: Boolean
    $isUsedForConsensus: Boolean
    $jsonMetadata: String
    $priority: Int
    $shouldResetToBeLabeledBy: Boolean
    $status: Status
    $toBeLabeledBy: [String]
) {{
  data: updatePropertiesInAsset(
    where: {{id: $assetID}},
    data: {{
      consensusMark: $consensusMark
      content: $content
      externalId: $externalId
      honeypotMark: $honeypotMark
      isHoneypot: $isHoneypot
      isUsedForConsensus: $isUsedForConsensus
      jsonMetadata: $jsonMetadata
      priority: $priority
      shouldResetToBeLabeledBy: $shouldResetToBeLabeledBy
      status: $status
      toBeLabeledBy: $toBeLabeledBy
    }}
  ) {{
    {ASSET_FRAGMENT}
  }}
}}
'''

GQL_DELETE_MANY_FROM_DATASET = f'''
mutation($assetIDs: [ID!]) {{
  data: deleteManyFromDataset(assetIDs: $assetIDs) {{
    {ASSET_FRAGMENT}
  }}
}}
'''
