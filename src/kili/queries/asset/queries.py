"""
Queries of asset queries
"""


def gql_assets(fragment):
    """
    Return the GraphQL assets query
    """
    return f"""
query($where: AssetWhere!, $first: PageSize!, $skip: Int!) {{
  data: assets(where: $where, skip: $skip, first: $first) {{
    {fragment}
  }}
}}
"""


GQL_ASSETS_COUNT = """
query($where: AssetWhere!) {
  data: countAssets(where: $where)
}
"""
