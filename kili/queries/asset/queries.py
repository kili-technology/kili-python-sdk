def gql_assets(fragment):
    return f'''
query($where: AssetWhere!, $first: PageSize!, $skip: Int!) {{
  data: assets(where: $where, skip: $skip, first: $first) {{
    {fragment}
  }}
}}
'''

GQL_ASSETS_COUNT = f'''
query($where: AssetWhere!) {{
  data: countAssets(where: $where)
}}
'''
