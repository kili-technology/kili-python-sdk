def gql_assets(fragment, fragment_label):
    if len(fragment_label) == 0:
        query = 'query($where: AssetWhere!, $first: PageSize!, $skip: Int!)'
        query_labels = ''
    else:
        query = 'query($where: AssetWhere!, $first: PageSize!, $skip: Int!, $labelWhere: LabelWhere!)'
        query_labels = f'''
    labels: labelsWhere(where: $labelWhere, skip: 0, first: 100) {{
        {fragment_label}
    }}
'''
    return f'''
{query} {{
  data: assets(where: $where, skip: $skip, first: $first) {{
    {fragment}
    {query_labels}
  }}
}}
'''

GQL_ASSETS_COUNT = f'''
query($where: AssetWhere!) {{
  data: countAssets(where: $where)
}}
'''
