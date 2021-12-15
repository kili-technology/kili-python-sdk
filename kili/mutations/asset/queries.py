"""
Queries of asset mutations
"""

from .fragments import ASSET_FRAGMENT


GQL_APPEND_MANY_TO_DATASET = f'''
mutation(
    $data: AppendManyToDatasetData!,
    $where: ProjectWhere!
  ) {{
  data: appendManyToDataset(
    data: $data,
    where: $where
  ) {{
    {ASSET_FRAGMENT}
  }}
}}
'''

GQL_APPEND_MANY_FRAMES_TO_DATASET = f'''
mutation(
    $data: AppendManyFramesToDatasetAsynchronouslyData!,
    $where: ProjectWhere!
  ) {{
  data: appendManyFramesToDatasetAsynchronously(
    data: $data,
    where: $where
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
