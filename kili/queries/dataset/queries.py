"""
Queries of project queries
"""


def gql_datasets(fragment: str):
    """
    Return the GraphQL projects query
    """
    return f'''
query($where: DatasetWhere!, $first: PageSize!, $skip: Int!) {{
  data: datasets(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
'''


GQL_DATASETS_COUNT = '''
query($where: DatasetWhere!) {
  data: countDatasets(where: $where)
}
'''
