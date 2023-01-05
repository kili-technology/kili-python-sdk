"""
label related mutations
"""

GQL_APPEND_MANY_LABELS = """
mutation appendManyLabels(
    $data: AppendManyLabelsData!
    $where: AssetWhere!
) {
  data: appendManyLabels(
    data: $data
    where: $where
  ) {
      id
    }
}
"""
