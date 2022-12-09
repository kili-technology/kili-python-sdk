"""
Api Key mutations
"""

from kili.graphql_client import GraphQLClient
from kili.helpers import format_result


def append_to_api_keys(client: GraphQLClient, email: str, api_key: str, name: str):
    fragment = """
  id
  createdAt
  name
  """
    mutation = f"""
  mutation (
    $data: AppendToApiKeysData!
    $where: UserWhere!
  ) {{
    data: appendToApiKeys(data: $data, where: $where) {{
      {fragment}
    }}
  }}
  """
    variables = {
        "data": {"key": api_key, "name": name},
        "where": {"email": email},
    }
    result = client.execute(mutation, variables)
    return format_result("data", result)
