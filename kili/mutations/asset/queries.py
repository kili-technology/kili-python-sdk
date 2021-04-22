from .fragments import ASSET_FRAGMENT


GQL_APPEND_MANY_TO_DATASET = f'''
mutation(
    $projectID: ID!,
    $contentArray: [String!],
    $externalIDArray: [String!],
    $isHoneypotArray: [Boolean!],
    $statusArray: [Status!],
    $jsonContentArray: [String!],
    $jsonMetadataArray: [String!]) {{
  data: appendManyToDataset(
    projectID: $projectID,
    contentArray: $contentArray,
    externalIDArray: $externalIDArray,
    isHoneypotArray: $isHoneypotArray,
    statusArray: $statusArray,
    jsonContentArray: $jsonContentArray,
    jsonMetadataArray: $jsonMetadataArray
  ) {{
    {ASSET_FRAGMENT}
  }}
}}
'''


GQL_UPDATE_PROPERTIES_IN_ASSETS = f'''
mutation(
    $whereArray: [AssetWhere!]!
    $dataArray: [AssetData!]!
) {{
  data: updatePropertiesInAssets(
    where: $whereArray,
    data: $dataArray
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
