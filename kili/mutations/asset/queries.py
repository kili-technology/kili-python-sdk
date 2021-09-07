from .fragments import ASSET_FRAGMENT


GQL_APPEND_MANY_TO_DATASET = f'''
mutation(
    $where: ProjectWhere!,
    $contentArray: [String!],
    $externalIDArray: [String!],
    $isHoneypotArray: [Boolean!],
    $statusArray: [Status!],
    $jsonContentArray: [String!],
    $jsonMetadataArray: [String!]) {{
  data: appendManyToDataset(
    where: $where,
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
mutation($where: AssetWhere!) {{
  data: deleteManyFromDataset(where: $where) {{
    {ASSET_FRAGMENT}
  }}
}}
'''
