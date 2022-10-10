"""
Queries of apiKey mutations
"""

from .fragments import API_KEY_FRAGMENT

GQL_APPEND_TO_API_KEYS = f"""
mutation(
  $data: AppendToApiKeysData!
  $where: UserWhere!
) {{
  data: appendToApiKeys(data: $data, where: $where) {{
    {API_KEY_FRAGMENT}
  }}
}}
"""
