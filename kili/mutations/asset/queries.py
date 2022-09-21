"""
Queries of asset mutations
"""

from kili.graphql.operations.asset.fragments import ASSET_FRAGMENT
from kili.mutations.project.fragments import PROJECT_FRAGMENT_ID

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
