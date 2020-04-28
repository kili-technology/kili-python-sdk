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
    $externalId: String
    $priority: Int
    $jsonMetadata: String
    $consensusMark: Float
    $honeypotMark: Float
    $toBeLabeledBy: [String!]
    $content: String
    $status: Status
    $isUsedForConsensus: Boolean
    $isHoneypot: Boolean
) {{
  data: updatePropertiesInAsset(
    where: {{id: $assetID}},
    data: {{
      externalId: $externalId
      priority: $priority
      jsonMetadata: $jsonMetadata
      consensusMark: $consensusMark
      honeypotMark: $honeypotMark
      toBeLabeledBy: $toBeLabeledBy
      content: $content
      status: $status
      isUsedForConsensus: $isUsedForConsensus
      isHoneypot: $isHoneypot
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
