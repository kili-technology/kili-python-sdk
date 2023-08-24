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
