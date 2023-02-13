"""Issue queries."""

import warnings
from typing import Dict, Generator, Iterable, List, Optional, overload

from typeguard import typechecked
from typing_extensions import Literal

from kili.graphql import QueryOptions
from kili.graphql.operations.issue.queries import IssueQuery, IssueWhere
from kili.helpers import disable_tqdm_if_as_generator


class QueriesIssue:
    """Set of Issue queries."""

    # pylint: disable=too-many-arguments,dangerous-default-value

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @overload
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
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
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
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

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
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
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
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        issues_gen = IssueQuery(self.auth.client)(where, fields, options)

        if as_generator:
            return issues_gen
        return list(issues_gen)

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
                (
                    "It is now required to provide a project_id when calling count_issues. This"
                    " change will be enforced from 01/02/2023"
                ),
                DeprecationWarning,
            )
        where = IssueWhere(project_id=project_id)
        return IssueQuery(self.auth.client).count(where)
