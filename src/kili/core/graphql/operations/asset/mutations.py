"""Assets related mutations."""

GQL_APPEND_MANY_ASSETS = """
mutation appendManyAssets(
    $data: AppendManyAssetsData!,
    $where: ProjectWhere!
  ) {
  data: appendManyAssets(
    data: $data,
    where: $where
  ) {
      id
  }
}
"""

GQL_APPEND_MANY_FRAMES_TO_DATASET = """
mutation(
    $data: AppendManyFramesToDatasetAsynchronouslyData!,
    $where: ProjectWhere!
  ) {
  data: appendManyFramesToDatasetAsynchronously(
    data: $data,
    where: $where
  ) {
    id
  }
}
"""
