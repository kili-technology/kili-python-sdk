from .fragments import ASSET_FRAGMENT


GQL_DELETE_DATASET_ASSETS = f'''
mutation(
    $assetIds: [ID!]
) {{
  data: deleteDatasetAssets(
    assetIds: $assetIds
  )
}}
'''

GQL_UPDATE_PROPERTIES_IN_DATASET_ASSETS = f'''
mutation(
    $whereArray: [DatasetAssetWhere!]!
    $dataArray: [DatasetAssetData!]!
) {{
  data: updatePropertiesInDatasetAssets(
    where: $whereArray,
    data: $dataArray
  ) {{
    {ASSET_FRAGMENT}
  }}
}}
'''
