"""
Helpers for the issue mutations
"""


from ...queries.issue import QueriesIssue


def get_issue_number(auth, project_id, type_):
    """Get the next available issue number

    Args:
        auth: Kili Auth
        project_id: Id of the project,
        type_: type of the issue to add
    """
    kili = QueriesIssue(auth)
    issues = kili.issues(project_id=project_id, disable_tqdm=True, fields=["type", "issueNumber"])
    if type_ == "ISSUE":
        issue_number = (
            max(
                [issue["issueNumber"] for issue in issues if issue["type"] == "ISSUE"],
                default=-1,
            )
            + 1
        )
    if type_ == "QUESTION":
        issue_number = (
            max(
                [issue["issueNumber"] for issue in issues if issue["type"] == "QUESTION"],
                default=-1,
            )
            + 1
        )

    return issue_number
