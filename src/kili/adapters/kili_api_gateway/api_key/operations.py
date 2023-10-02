"""GraphQL Asset operations."""


def get_api_keys_query(fragment: str) -> str:
    """Return the GraphQL apiKeys query."""
    return f"""
        query apiKeys($where: ApiKeyWhere!, $first: PageSize!, $skip: Int!) {{
          data: apiKeys(where: $where, skip: $skip, first: $first) {{
            {fragment}
          }}
        }}
        """


GQL_COUNT_API_KEYS = """
query countApiKeys($where: ApiKeyWhere!) {
    data: countApiKeys(where: $where)
}
"""

GQL_API_KEY_EXPIRY_DATE = """
    query apiKeys($where: ApiKeyWhere!) {
        data: apiKeys(where: $where, skip: 0, first: 1) {
            expiryDate
        }
    }
    """
