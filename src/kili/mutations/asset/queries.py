"""
Queries of asset mutations
"""

from kili.mutations.project.fragments import PROJECT_FRAGMENT_ID

GQL_UPDATE_PROPERTIES_IN_ASSETS = """
mutation(
    $whereArray: [AssetWhere!]!
    $dataArray: [AssetData!]!
) {
  data: updatePropertiesInAssets(
    where: $whereArray,
    data: $dataArray
  ) {
    id
  }
}
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
