"""Queries of label mutations."""

from .fragments import LABEL_FRAGMENT_ID

GQL_APPEND_TO_LABELS = f"""
mutation(
    $data: AppendToLabelsData!
    $where: AssetWhere!
) {{
  data: appendToLabels(
    data: $data
    where: $where
  ) {{
      {LABEL_FRAGMENT_ID}
  }}
}}
"""
