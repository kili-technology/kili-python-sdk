"""
Queries of apiKey mutations
"""

GQL_APPEND_TO_API_KEYS = """
mutation(
  $data: AppendToApiKeysData!
  $where: UserWhere!
) {{
  data: appendToApiKeys(data: $data, where: $where) {{
    id
  }}
}}
"""
