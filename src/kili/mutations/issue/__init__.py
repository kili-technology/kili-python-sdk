"""
Issue mutations
"""

from typing import Dict, List, Optional, cast

from typeguard import typechecked
from typing_extensions import Literal

from kili.graphql import QueryOptions
from kili.graphql.operations.label.queries import LabelQuery, LabelWhere

from ...helpers import format_result
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
    ) -> Dict:
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
            options = QueryOptions(disable_tqdm=True)
            where = LabelWhere(
                project_id=project_id,
                label_id=label_id,
            )
            asset_id = cast(
                List[Dict],
                list(
                    LabelQuery(self.auth.client)(
                        where=where, fields=["labelOf.id"], options=options
                    )
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
        if text:
            variables["data"]["text"] = text

        result = self.auth.client.execute(GQL_APPEND_TO_ISSUES, variables)
        return format_result("data", result)
