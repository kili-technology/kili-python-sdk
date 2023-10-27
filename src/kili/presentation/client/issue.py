# pylint: disable=too-many-arguments
"""Client presentation methods for issues."""

from itertools import repeat
from typing import Dict, Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.issue import IssueFilters, IssueStatus, IssueType
from kili.domain.label import LabelId
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.presentation.client.helpers.common_validators import (
    assert_all_arrays_have_same_size,
    disable_tqdm_if_as_generator,
)
from kili.use_cases.issue import IssueUseCases
from kili.use_cases.issue.types import IssueToCreateUseCaseInput
from kili.utils.logcontext import for_all_methods, log_call

from .base import BaseClientMethods


@for_all_methods(log_call, exclude=["__init__"])
class IssueClientMethods(BaseClientMethods):
    """Methods attached to the Kili client, to run actions on issues."""

    @typechecked
    def create_issues(
        self,
        project_id: str,
        label_id_array: List[str],
        object_mid_array: Optional[List[Optional[str]]] = None,
        text_array: Optional[List[Optional[str]]] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Create an issue.

        Args:
            project_id: Id of the project.
            label_id_array: List of Ids of the labels to add an issue to.
            object_mid_array: List of mids of the objects in the labels to associate the issues to.
            text_array: List of texts to associate to the issues.

        Returns:
            A list of dictionaries with the `id` key of the created issues.
        """
        assert_all_arrays_have_same_size([label_id_array, object_mid_array, text_array])
        issues = [
            IssueToCreateUseCaseInput(label_id=LabelId(label_id), object_mid=object_mid, text=text)
            for (label_id, object_mid, text) in zip(
                label_id_array,
                object_mid_array or repeat(None),
                text_array or repeat(None),
            )
        ]
        issue_service = IssueUseCases(self.kili_api_gateway)
        issue_ids = issue_service.create_issues(project_id=ProjectId(project_id), issues=issues)
        return [{"id": issue_id} for issue_id in issue_ids]

    @typechecked
    def count_issues(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_id_in: Optional[List[str]] = None,
        issue_type: Optional[IssueType] = None,
        status: Optional[IssueStatus] = None,
    ) -> int:
        """Count and return the number of issues with the given constraints.

        Args:
            project_id: Project ID the issue belongs to.
            asset_id: Asset id whose returned issues are associated to.
            asset_id_in: List of asset ids whose returned issues are associated to.
            issue_type: Type of the issue to return. An issue object both
                represents issues and questions in the app.
            status: Status of the issues to return.

        Returns:
            The number of issues that match the given constraints.
        """
        if asset_id and asset_id_in:
            raise ValueError(
                "You cannot provide both `asset_id` and `asset_id_in` at the same time."
            )
        return IssueUseCases(self.kili_api_gateway).count_issues(
            IssueFilters(
                project_id=ProjectId(project_id),
                asset_id=asset_id,
                asset_id_in=asset_id_in,
                issue_type=issue_type,
                status=status,
            )
        )

    @overload
    def issues(
        self,
        project_id: str,
        fields: ListOrTuple[str] = (
            "id",
            "createdAt",
            "status",
            "type",
            "assetId",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        asset_id: Optional[str] = None,
        asset_id_in: Optional[List[str]] = None,
        issue_type: Optional[IssueType] = None,
        status: Optional[IssueStatus] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def issues(
        self,
        project_id: str,
        fields: ListOrTuple[str] = (
            "id",
            "createdAt",
            "status",
            "type",
            "assetId",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        asset_id: Optional[str] = None,
        asset_id_in: Optional[List[str]] = None,
        issue_type: Optional[IssueType] = None,
        status: Optional[IssueStatus] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @typechecked
    def issues(
        self,
        project_id: str,
        fields: ListOrTuple[str] = (
            "id",
            "createdAt",
            "status",
            "type",
            "assetId",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        asset_id: Optional[str] = None,
        asset_id_in: Optional[List[str]] = None,
        issue_type: Optional[IssueType] = None,
        status: Optional[IssueStatus] = None,
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
                "You cannot provide both `asset_id` and `asset_id_in` at the same time."
            )

        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm=disable_tqdm, first=first, skip=skip)
        issues_gen = IssueUseCases(self.kili_api_gateway).list_issues(
            IssueFilters(
                project_id=ProjectId(project_id),
                asset_id=asset_id,
                asset_id_in=asset_id_in,
                issue_type=issue_type,
                status=status,
            ),
            fields=fields,
            options=options,
        )
        if as_generator:
            return issues_gen
        return list(issues_gen)
