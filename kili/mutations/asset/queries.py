"""
Queries of asset mutations
"""

from kili.mutations.project.fragments import PROJECT_FRAGMENT_ID

from .fragments import ASSET_FRAGMENT

GQL_APPEND_MANY_TO_DATASET = f"""
mutation(
    $data: AppendManyToDatasetData!,
    $where: ProjectWhere!
  ) {{
  data: appendManyToDataset(
    data: $data,
    where: $where
  ) {{
    {PROJECT_FRAGMENT_ID}
  }}
}}
"""

GQL_APPEND_MANY_FRAMES_TO_DATASET = f"""
mutation(
    $data: AppendManyFramesToDatasetAsynchronouslyData!,
    $where: ProjectWhere!
  ) {{
  data: appendManyFramesToDatasetAsynchronously(
    data: $data,
    where: $where
  ) {{
    {PROJECT_FRAGMENT_ID}
  }}
}}
"""


GQL_UPDATE_PROPERTIES_IN_ASSETS = f"""
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
"""

GQL_DELETE_MANY_FROM_DATASET = f"""
mutation($where: AssetWhere!) {{
  data: deleteManyFromDataset(where: $where) {{
    {PROJECT_FRAGMENT_ID}
  }}
}}
"""

GQL_ADD_ALL_LABELED_ASSETS_TO_REVIEW = f"""
mutation($where: AssetWhere!) {{
  data: addAllLabeledAssetsToReview(where: $where) {{
    {PROJECT_FRAGMENT_ID}
  }}
}}
"""

GQL_SEND_BACK_ASSETS_TO_QUEUE = f"""
mutation($where: AssetWhere!) {{
  data: sendBackAssetsToQueue(where: $where) {{
    {PROJECT_FRAGMENT_ID}
  }}
}}
"""
