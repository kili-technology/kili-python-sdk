"""
Queries of comment mutations
"""

from .fragments import COMMENT_FRAGMENT

GQL_APPEND_TO_COMMENTS = f"""
mutation(
    $data: AppendToCommentsData!
    $where: IssueWhere!
) {{
  data: appendToComments(
    data: $data
    where: $where
  ) {{
    {COMMENT_FRAGMENT}
  }}
}}
"""
