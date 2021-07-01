from .fragments import ASSET_FRAGMENT

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
