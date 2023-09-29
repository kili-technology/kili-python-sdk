"""GraphQL Issues operations."""

GQL_CREATE_ISSUES = """
mutation createIssues(
    $issues: [IssueToCreate!]!
    $where: AssetWhere!
) {
  data: createIssues(
    issues: $issues
    where: $where
  ) {
    id
  }
}
"""

GQL_COUNT_ISSUES = """
query countIssues($where: IssueWhere!) {
    data: countIssues(where: $where)
}
"""


def get_issues_query(fragment: str) -> str:
    """Return the GraphQL issues query."""
    return f"""
    query issues($where: IssueWhere!, $first: PageSize!, $skip: Int!) {{
        data: issues(where: $where, first: $first, skip: $skip) {{
            {fragment}
        }}
    }}
    """
