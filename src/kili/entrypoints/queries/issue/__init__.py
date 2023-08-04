"""Issue queries."""
from typing import Dict, Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.core.graphql import QueryOptions
from kili.core.graphql.operations.issue.queries import IssueQuery, IssueWhere
from kili.core.helpers import disable_tqdm_if_as_generator
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class QueriesIssue(BaseOperationEntrypointMixin):
    """Set of Issue queries."""

    # pylint: disable=too-many-arguments,dangerous-default-value

    @overload
    def issues(
        self,
        project_id: str,
        fields: List[str] = [
            "id",
            "createdAt",
            "status",
            "type",
        ],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        asset_id: Optional[str] = None,
        asset_id_in: Optional[List[str]] = None,
        issue_type: Optional[Literal["QUESTION", "ISSUE"]] = None,
        status: Optional[Literal["OPEN", "SOLVED"]] = None,
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
            "status",
            "type",
        ],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        asset_id: Optional[str] = None,
        asset_id_in: Optional[List[str]] = None,
        issue_type: Optional[Literal["QUESTION", "ISSUE"]] = None,
        status: Optional[Literal["OPEN", "SOLVED"]] = None,
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
            "status",
            "type",
            "assetId",
        ],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        asset_id: Optional[str] = None,
        asset_id_in: Optional[List[str]] = None,
        issue_type: Optional[Literal["QUESTION", "ISSUE"]] = None,
        status: Optional[Literal["OPEN", "SOLVED"]] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        # pylint: disable=line-too-long
        """Get a generator or a list of issues that match a set of criteria.

        !!! Info "Issues or Questions"
            An `Issue` object both represent an issue and a question in the app.
            To create them, two different methods are provided: `create_issues` and `create_questions`.
            However to query issues and questions, we currently provide this unique method that retrieves both of them.

        Args:
            project_id: Project ID the issue belongs to.
            asset_id: Id of the asset whose returned issues are associated to.
            asset_id_in: List of Ids of assets whose returned issues are associated to.
            issue_type: Type of the issue to return. An issue object both represents issues and questions in the app.
            status: Status of the issues to return.
            fields: All the fields to request among the possible fields for the assets.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#issue) for all possible fields.
            first: Maximum number of issues to return.
            skip: Number of issues to skip (they are ordered by their date of creation, first to last).
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the issues is returned.
        Returns:
            An iterable of issues objects represented as `dict`.

        Examples:
            >>> kili.issues(project_id=project_id, fields=['author.email']) # List all issues of a project and their authors
        """

        if asset_id and asset_id_in:
            raise ValueError(
                "You cannot provide both `asset_id` and `asset_id_in` at the same time"
            )
        where = IssueWhere(
            project_id=project_id,
            asset_id=asset_id,
            asset_id_in=asset_id_in,
            issue_type=issue_type,
            status=status,
        )
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        issues_gen = IssueQuery(self.graphql_client, self.http_client)(where, fields, options)
        if as_generator:
            return issues_gen
        return list(issues_gen)

    @typechecked
    def count_issues(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_id_in: Optional[List[str]] = None,
        issue_type: Optional[Literal["QUESTION", "ISSUE"]] = None,
        status: Optional[Literal["OPEN", "SOLVED"]] = None,
    ) -> int:
        """Count and return the number of issues with the given constraints.

        Args:
            project_id: Project ID the issue belongs to.
            asset_id: Asset id whose returned issues are associated to.
            asset_id_in: List of asset ids whose returned issues are associated to.
            issue_type: Type of the issue to return. An issue object both
                represents issues and questions in the app
            status: Status of the issues to return.
        Returns:
            The number of issues with the parameters provided
        """
        if asset_id and asset_id_in:
            raise ValueError(
                "You cannot provide both `asset_id` and `asset_id_in` at the same time"
            )
        where = IssueWhere(
            project_id=project_id,
            asset_id=asset_id,
            asset_id_in=asset_id_in,
            issue_type=issue_type,
            status=status,
        )
        return IssueQuery(self.graphql_client, self.http_client).count(where)
