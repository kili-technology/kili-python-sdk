"""
Queries of issue queries
"""


def gql_issues(fragment):
    """
    Return the GraphQL issues query
    """
    return f"""
query ($where: IssueWhere!, $first: PageSize!, $skip: Int!) {{
  data: issues(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
"""


GQL_ISSUES_COUNT = """
query($where: IssueWhere!) {
  data: countIssues(where: $where)
}
"""
