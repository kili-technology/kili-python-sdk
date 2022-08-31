"""
Issue mutations
"""

from typing import Dict, List, Optional, cast

from typeguard import typechecked
from typing_extensions import Literal

from ...helpers import format_result
from ...queries.label import QueriesLabel
from ..comment.queries import GQL_APPEND_TO_COMMENTS
from .helpers import get_issue_number
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

    @typechecked
    def append_to_issues(
        self,
        label_id: str,
        project_id: str,
        object_mid: Optional[str] = None,
        text: Optional[str] = None,
        type_: Literal["ISSUE", "QUESTION"] = "ISSUE",
    ) -> dict:
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
        try:
            asset_id = cast(
                List[Dict],
                QueriesLabel(self.auth).labels(
                    project_id=project_id,
                    label_id=label_id,
                    fields=["labelOf.id"],
                    disable_tqdm=True,
                )[0]["labelOf"]["id"],
            )
        except:
            # pylint: disable=raise-missing-from
            raise ValueError(
                f"Label ID {label_id} does not exist in the project of ID {project_id}"
            )
        variables = {
            "data": {
                "issueNumber": issue_number,
                "labelID": label_id,
                "objectMid": object_mid,
                "type": type_,
            },
            "where": {"id": asset_id},
        }
        result = self.auth.client.execute(GQL_APPEND_TO_ISSUES, variables)
        formated_result = format_result("data", result)
        issue_id = formated_result["id"]

        if text:
            variables = {
                "data": {
                    "text": text,
                    "inReview": False,
                },
                "where": {
                    "id": issue_id,
                },
            }
            result = self.auth.client.execute(GQL_APPEND_TO_COMMENTS, variables)

        return formated_result
