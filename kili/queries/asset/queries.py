TYPES_ALLOWED = '["DEFAULT", "AUTOSAVE", "REVIEW"]'

def gql_assets(fragment, fragment_label, where_label):
    return f'''
query($where: AssetWhere!, $first: PageSize!, $skip: Int!) {{
  data: assets(where: $where, skip: $skip, first: $first) {{
    {fragment}
    labelsWhere(where: {{ typeIn: {TYPES_ALLOWED} }}, skip: 0, first: 100) {{
        {fragment_label}
    }}
  }}
}}
'''

GQL_ASSETS_COUNT = f'''
query($where: AssetWhere!) {{
  data: countAssets(where: $where)
}}
'''
