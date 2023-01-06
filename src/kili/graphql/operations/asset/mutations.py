"""
Assets related mutations
"""

GQL_APPEND_MANY_TO_DATASET = """
mutation appendManyToDataset(
    $data: AppendManyToDatasetData!,
    $where: ProjectWhere!
  ) {
  data: appendManyToDataset(
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
