"""Issue queries."""

import warnings
from typing import Iterable, List, Optional

from typeguard import typechecked

from kili.graphql import QueryOptions
from kili.graphql.operations.issue.queries import IssueQuery, IssueWhere


class QueriesIssue:
    """Set of Issue queries."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    # pylint: disable=dangerous-default-value
    @typechecked
    def issues(
        self,
        project_id: str,
        fields: List[str] = [
            "id",
            "createdAt",
            "hasBeenSeen",
            "issueNumber",
            "status",
            "type",
        ],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        as_generator: bool = False,
    ) -> Iterable[dict]:
        # pylint: disable=line-too-long
        """Get a generator or a list of issues that match a set of criteria.

        Args:
            project_id: Project ID the issue belongs to.
            fields: All the fields to request among the possible fields for the assets.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#issue) for all possible fields.
            first: Maximum number of issues to return.
            skip: Number of issues to skip (they are ordered by their date of creation, first to last).
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the issues is returned.

        Returns:
            A result object which contains the query if it was successful,
                or an error message.

        Examples:
            >>> kili.issues(project_id=project_id, fields=['author.email']) # List all issues of a project and their authors
        """
        where = IssueWhere(project_id=project_id)
        options = QueryOptions(disable_tqdm, first, skip, as_generator)
        return IssueQuery(self.auth.client)(where, fields, options)

    @typechecked
    def count_issues(self, project_id: Optional[str] = None) -> int:
        """Count and return the number of api keys with the given constraints.

        Args:
            project_id: Project ID the issue belongs to.

        Returns:
            The number of issues with the parameters provided

        """
        if not project_id:
            warnings.warn(
                "It is now required to provide a project_id when calling count_issues. This change"
                " will be enforced from 01/02/2023",
                DeprecationWarning,
            )
        where = IssueWhere(project_id=project_id)
        return IssueQuery(self.auth.client).count(where)
