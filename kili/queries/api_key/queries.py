"""
Queries of asset queries
"""


def gql_api_keys(fragment):
    """
    Return the GraphQL assets query
    """
    return f"""
query($where: ApiKeyWhere!, $first: PageSize!, $skip: Int!) {{
  data: apiKeys(where: $where, skip: $skip, first: $first) {{
    {fragment}
  }}
}}
"""


GQL_API_KEYS_COUNT = """
query($where: ApiKeyWhere!) {
  data: countApiKeys(where: $where)
}
"""
