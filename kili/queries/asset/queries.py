def gql_assets(fragment, fragment_label):
    return f'''
query($where: AssetWhere!, $first: PageSize!, $skip: Int!, $labelWhere: LabelWhere!) {{
  data: assets(where: $where, skip: $skip, first: $first) {{
    {fragment}
    labels: labelsWhere(where: $labelWhere, skip: 0, first: 100) {{
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
