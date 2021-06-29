def gql_assets(fragment):
    return f'''
query($where: DatasetAssetWhere!, $first: PageSize!, $skip: Int!) {{
  data: datasetAssets(where: $where, skip: $skip, first: $first) {{
    {fragment}
  }}
}}
'''


GQL_DATASET_ASSETS_COUNT = f'''
query($where: DatasetAssetWhere!) {{
  data: countDatasetAssets(where: $where)
}}
'''
