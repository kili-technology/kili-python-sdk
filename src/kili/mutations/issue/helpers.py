"""
Helpers for the issue mutations
"""


from kili.authentication import KiliAuth

from ...queries.issue import QueriesIssue


def get_issue_number(auth: KiliAuth, project_id: str, type_: str):
    """Get the next available issue number

    Args:
        auth: Kili Auth
        project_id: Id of the project
        type_: type of the issue to add
    """
    kili = QueriesIssue(auth)
    issues = kili.issues(project_id=project_id, disable_tqdm=True, fields=["type", "issueNumber"])
    issue_number = (
        max(
            [issue["issueNumber"] for issue in issues if issue["type"] == type_],
            default=-1,
        )
        + 1
    )

    return issue_number
