"""
Queries of issue mutations
"""

from .fragments import ISSUE_FRAGMENT

GQL_APPEND_TO_ISSUES = f"""
mutation(
    $data: AppendToIssuesData!
    $where: AssetWhere!
) {{
  data: appendToIssues(
    data: $data
    where: $where
  ) {{
    {ISSUE_FRAGMENT}
  }}
}}
"""

GQL_CREATE_ISSUES = f"""
mutation createIssues(
    $issues: [IssueToCreate!]!
    $where: AssetWhere!
) {{
  data: createIssues(
    issues: $issues
    where: $where
  ) {{
    {ISSUE_FRAGMENT}
  }}
}}
"""
