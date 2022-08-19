"""
Issue mutations
"""

from typing import Literal, Optional
from typeguard import typechecked
from ..comment import MutationsComment
from .helpers import get_issue_number
from ...helpers import Compatible, format_result
from .queries import GQL_APPEND_TO_ISSUES


class MutationsIssue:
    """Set of Issue mutations."""

    # pylint: disable=too-few-public-methods,too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @Compatible(["v1", "v2"])
    @typechecked
    def append_to_issues(
        self,
        label_id: str,
        project_id: str,
        object_mid: Optional[str] = None,
        text: Optional[str] = None,
        type_: Literal["ISSUE", "QUESTION"] = "ISSUE",
    ):
        """Create an issue.

        Args:
            label_id: Id of the label to add an issue to
            object_mid: Mid of the object in the label to associate the issue to
            type_: type of the issue to add. Can be either "ISSUE" or "QUESTION"
            text: If given, write a comment related to the issue
            project_id: Id of the project

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        issue_number = get_issue_number(self.auth, project_id, type_)
        variables = {
            "data": {
                "issueNumber": issue_number,
                "labelID": label_id,
                "objectMid": object_mid,
                "type": type_,
            },
            "where": {"label": {"id": label_id}, "project": {"id": project_id}},
        }
        result = self.auth.client.execute(GQL_APPEND_TO_ISSUES, variables)
        formated_result = format_result("data", result)
        issue_id = formated_result["id"]

        if text:
            MutationsComment(self.auth).append_to_comments(
                text=text, in_review=False, issue_id=issue_id
            )

        return formated_result
