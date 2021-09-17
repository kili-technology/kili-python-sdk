"""
Queries of dataset asset mutations
"""

from .fragments import ASSET_FRAGMENT


GQL_DELETE_DATASET_ASSETS = '''
mutation(
    $where: DatasetAssetWhere!
) {
  data: deleteDatasetAssets(
    where: $where
  )
}
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
