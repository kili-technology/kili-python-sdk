from .fragments import ASSET_FRAGMENT

GQL_DELETE_ASSETS_BY_EXTERNAL_ID = f'''
mutation($projectID: ID!, $externalID: String!) {{
  data: deleteAssetsByExternalId(projectID: $projectID, externalID: $externalID) {{
    {ASSET_FRAGMENT}
  }}
}}
'''

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

GQL_UPDATE_ASSET = f'''
mutation(
    $assetID: ID!,
    $projectID: ID!,
    $content: String!,
    $externalID: String,
    $isHoneypot: Boolean,
    $consensusMark: Float,
    $honeypotMark: Float,
    $status:  Status!,
    $jsonMetadata: String
) {{
  data: updateAsset(
    assetID: $assetID,
    projectID: $projectID,
    content: $content,
    externalID: $externalID,
    isHoneypot: $isHoneypot,
    consensusMark: $consensusMark,
    honeypotMark: $honeypotMark,
    status: $status,
    jsonMetadata: $jsonMetadata) {{
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
    }}
  ) {{
    {ASSET_FRAGMENT}
  }}
}}
'''

GQL_DELETE_FROM_DATASET = f'''
mutation($assetID: ID!) {{
  data: deleteFromDataset(assetID: $assetID) {{
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
