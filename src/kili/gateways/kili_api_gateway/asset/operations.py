"""GraphQL Asset operations."""


def get_asset_query(fragment: str):
    """Return the GraphQL assets query."""
    return f"""
        query assets($where: AssetWhere!, $first: PageSize!, $skip: Int!) {{
            data: assets(where: $where, skip: $skip, first: $first) {{
                {fragment}
            }}
        }}
        """


GQL_COUNT_ASSETS = """
query countAssets($where: AssetWhere!) {
    data: countAssets(where: $where)
}
"""
