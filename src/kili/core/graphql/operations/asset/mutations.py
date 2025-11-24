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

GQL_SET_ASSET_CONSENSUS = """
mutation setAssetConsensus(
    $assetId: ID,
    $externalId: String,
    $projectId: ID!,
    $isConsensus: Boolean!
  ) {
  data: setAssetConsensus(
    assetId: $assetId,
    externalId: $externalId,
    projectId: $projectId,
    isConsensus: $isConsensus
  )
}
"""
