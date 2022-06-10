"""
Comment mutations
"""

from typing import Optional
from typeguard import typechecked

from ...helpers import Compatible, format_result
from .queries import GQL_APPEND_TO_COMMENTS


class MutationsComment:
    """Set of Comment mutations."""

    # pylint: disable=too-few-public-methods,too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @Compatible(["v1", "v2"])
    @typechecked
    def append_to_comments(
        self,
        text: str,
        in_review: bool,
        issue_id: str,
    ):
        """Create a comment.

        Args:
            text :
            in_review :
            issue_id :

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        variables = {
            "data": {
                "text": text,
                "inReview": in_review,
            },
            "where": {
                "id": issue_id,
            },
        }
        result = self.auth.client.execute(GQL_APPEND_TO_COMMENTS, variables)
        return format_result("data", result)
