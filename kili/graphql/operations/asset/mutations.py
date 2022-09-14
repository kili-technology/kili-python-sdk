"""
Assets related mutations
"""
from kili.graphql.operations.asset.fragments import PROJECT_FRAGMENT_ID

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
