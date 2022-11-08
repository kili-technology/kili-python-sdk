"""
label related mutations
"""

from kili.graphql.operations.label.fragments import LABEL_FRAGMENT_ID

GQL_APPEND_MANY_LABELS = f"""
mutation(
    $data: AppendManyLabelsData!
    $where: AssetWhere!
) {{
  data: appendManyLabels(
    data: $data
    where: $where
  ) {{
      {LABEL_FRAGMENT_ID}
  }}
}}
"""
