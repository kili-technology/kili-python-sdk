"""Queries of label mutations."""

from .fragments import LABEL_FRAGMENT, LABEL_FRAGMENT_ID

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


GQL_CREATE_HONEYPOT = f"""
mutation(
    $data: CreateHoneypotData!
    $where: AssetWhere!
) {{
  data: createHoneypot(
    data: $data
    where: $where
  ) {{
      {LABEL_FRAGMENT}
  }}
}}
"""
