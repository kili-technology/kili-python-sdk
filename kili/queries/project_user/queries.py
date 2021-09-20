"""
Queries of project user queries
"""


def gql_project_users(fragment):
    """
    Return the GraphQL projectUsers query
    """
    return f'''
query($where: ProjectUserWhere!, $first: PageSize!, $skip: Int!) {{
  data: projectUsers(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
'''


GQL_PROJECT_USERS_COUNT = '''
query($where: ProjectUserWhere!) {
  data: countProjectUsers(where: $where)
}
'''
