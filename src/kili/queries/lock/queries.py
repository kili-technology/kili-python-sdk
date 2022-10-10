"""
Queries of lock queries
"""


def gql_locks(fragment):
    """
    Return the GraphQL locks query
    """
    return f"""
query($where: LockWhere!, $first: PageSize!, $skip: Int!) {{
  data: locks(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
"""


GQL_LOCKS_COUNT = """
query($where: LockWhere!) {
  data: countLocks(where: $where)
}
"""
