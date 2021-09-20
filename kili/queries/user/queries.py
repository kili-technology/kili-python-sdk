"""
Queries of user queries
"""


def gql_users(fragment):
    """
    Return the GraphQL users query
    """
    return f'''
query($where: UserWhere!, $first: PageSize!, $skip: Int!) {{
  data: users(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
'''


GQL_USERS_COUNT = '''
query($where: UserWhere!) {
  data: countUsers(where: $where)
}
'''
