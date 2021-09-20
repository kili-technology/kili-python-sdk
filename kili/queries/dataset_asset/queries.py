"""
Queries of dataset asset queries
"""


def gql_assets(fragment):
    """
    Return the GraphQL datasetAssets query
    """
    return f'''
query($where: DatasetAssetWhere!, $first: PageSize!, $skip: Int!) {{
  data: datasetAssets(where: $where, skip: $skip, first: $first) {{
    {fragment}
  }}
}}
'''


GQL_DATASET_ASSETS_COUNT = '''
query($where: DatasetAssetWhere!) {
  data: countDatasetAssets(where: $where)
}
'''
