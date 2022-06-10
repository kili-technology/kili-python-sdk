"""
Issue mutations
"""

from typing import Optional
from typeguard import typechecked

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
        issue_number: int,
        label_id: str,
        object_mid: Optional[str],
        type_: str,
        external_id: str,
        project_id: str,
    ):
        """Create a issue.

        Args:
            issue_number :
            label_id :
            object_mid :
            type_ :
            external_id :
            project_id :

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        variables = {
            "data": {
                "issueNumber": issue_number,
                "labelID": label_id,
                "objectMid": object_mid,
                "type": type_,
            },
            "where": {
                "externalIdStrictlyIn": external_id,
                "project": {"id": project_id},
            },
        }
        result = self.auth.client.execute(GQL_APPEND_TO_ISSUES, variables)
        return format_result("data", result)
