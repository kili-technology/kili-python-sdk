"""
GraphQL Queries of API keys
"""


from typing import NamedTuple, Optional

from kili.graphql import GraphQLQuery

from ....types import ApiKey


class APIKeyWhere(NamedTuple):
    """
    Tuple to be passed to the APIKeyQuery to restrict the query
    """

    api_key_id: Optional[str] = None
    user_id: Optional[str] = None
    api_key: Optional[str] = None


def where_payload_builder(where: APIKeyWhere):
    """Build the GraphQL Where payload sent in the resolver from the SDK APIKeyWhere"""
    return {
        "user": {"id": where.user_id, "apiKey": where.api_key},
        "id": where.api_key_id,
    }


def query(fragment):
    """
    Return the GraphQL apiKeys query
    """
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

APIKeyQuery = GraphQLQuery(
    _type=ApiKey,
    query=query,
    count_query=GQL_COUNT_API_KEYS,
    where_payload_builder=where_payload_builder,
)
