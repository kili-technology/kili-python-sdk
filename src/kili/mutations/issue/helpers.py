"""
Helpers for the issue mutations
"""


from kili.authentication import KiliAuth
from kili.graphql import QueryOptions
from kili.graphql.operations.issue.queries import IssueQuery, IssueWhere


def get_issue_number(auth: KiliAuth, project_id: str, type_: str):
    """Get the next available issue number

    Args:
        auth: Kili Auth
        project_id: Id of the project
        type_: type of the issue to add
    """
    issues = IssueQuery(auth.client)(
        IssueWhere(project_id=project_id), ["type", "issueNumber"], QueryOptions(disable_tqdm=True)
    )
    issue_number = (
        max(
            (issue["issueNumber"] for issue in issues if issue["type"] == type_),
            default=-1,
        )
        + 1
    )

    return issue_number
