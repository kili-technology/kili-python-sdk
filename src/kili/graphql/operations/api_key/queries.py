"""
Queries of asset queries
"""


from typing import NamedTuple, Optional

from kili.graphql import GraphQLQuery

from ....types import ApiKey


class APIKeyWhere(NamedTuple):
    api_key_id: Optional[str] = None
    user_id: Optional[str] = None
    api_key: Optional[str] = None


def where_payload_builder(where: APIKeyWhere):
    return {
        "user": {"id": where.user_id, "apiKey": where.api_key},
        "id": where.api_key_id,
    }


def query(fragment):
    return f"""
  query apiKeys($where: ApiKeyWhere!, $first: PageSize!, $skip: Int!) {{
    data: apiKeys(where: $where, skip: $skip, first: $first) {{
      {fragment}
    }}
  }}
  """


count_query = """
  query countApiKeys($where: ApiKeyWhere!) {
    data: countApiKeys(where: $where)
  }
  """

APIKeyQuery = GraphQLQuery(
    _type=ApiKey, query=query, count_query=count_query, where_payload_builder=where_payload_builder
)
