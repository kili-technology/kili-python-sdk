# pylint: disable=too-many-arguments
"""Client presentation methods for issues."""

from collections.abc import Generator, Iterable
from itertools import repeat
from typing import Any, Literal, Optional, overload

from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.issue import IssueFilters, IssueId, IssueStatus, IssueType
from kili.domain.label import LabelId
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.presentation.client.helpers.common_validators import (
    assert_all_arrays_have_same_size,
    disable_tqdm_if_as_generator,
    resolve_disable_tqdm,
)
from kili.presentation.client.helpers.filter_conversion import (
    extract_step_ids_from_project_steps,
)
from kili.use_cases.issue import IssueUseCases
from kili.use_cases.issue.types import IssueToCreateUseCaseInput
from kili.use_cases.project.project import ProjectUseCases
from kili.utils.logcontext import for_all_methods, log_call

from .base import BaseClientMethods


# The current steps step_name_in names, by id; step_id_in as given otherwise. A step removed from
# the workflow is not among the project's steps: its issues are found by its id only.
def _resolve_step_ids(
    kili_api_gateway: KiliAPIGateway,
    project_id: str,
    step_id_in: Optional[list[str]],
    step_name_in: Optional[list[str]],
) -> Optional[list[str]]:
    if step_id_in is not None and step_name_in is not None:
        raise ValueError("Filters step_id_in and step_name_in both given: use only one of them.")
    if step_name_in is None:
        return step_id_in
    project_steps, _ = ProjectUseCases(kili_api_gateway).get_project_steps_and_version(project_id)
    step_names = {step["name"] for step in project_steps}
    unmatched_names = [name for name in step_name_in if name not in step_names]
    if unmatched_names:
        raise ValueError(
            f"The following step names match no current step of the project: {unmatched_names}. "
            "Issues raised in a step since removed from the workflow are filtered by its id: "
            "use step_id_in with the issues' stepId."
        )
    return extract_step_ids_from_project_steps(
        project_steps=project_steps, step_name_in=step_name_in
    )


@for_all_methods(log_call, exclude=["__init__"])
class IssueClientMethods(BaseClientMethods):
    """Methods attached to the Kili client, to run actions on issues."""

    @typechecked
    def create_issues(
        self,
        project_id: str,
        label_id_array: list[str],
        object_mid_array: Optional[list[Optional[str]]] = None,
        text_array: Optional[list[Optional[str]]] = None,
    ) -> list[dict[Literal["id"], str]]:
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
                strict=False,
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
        asset_id_in: Optional[list[str]] = None,
        issue_type: Optional[IssueType] = None,
        status: Optional[IssueStatus] = None,
        step_id_in: Optional[list[str]] = None,
        step_name_in: Optional[list[str]] = None,
    ) -> int:
        """Count and return the number of issues with the given constraints.

        Args:
            project_id: Project ID the issue belongs to.
            asset_id: Asset id whose returned issues are associated to.
            asset_id_in: List of asset ids whose returned issues are associated to.
            issue_type: Type of the issue to return. An issue object both
                represents issues and questions in the app.
            status: Status of the issues to return.
            step_id_in: Ids of the steps the returned issues were raised in.
                Exclusive with `step_name_in`.
            step_name_in: Names of the project's current steps the returned issues were raised in.
                Only applicable if the project uses the multi-step or multi-group workflow.
                A step removed from the workflow is filtered by its id, with `step_id_in`.
                Exclusive with `step_id_in`.

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
                step_id_in=_resolve_step_ids(
                    self.kili_api_gateway, project_id, step_id_in, step_name_in
                ),
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
        asset_id_in: Optional[list[str]] = None,
        issue_type: Optional[IssueType] = None,
        status: Optional[IssueStatus] = None,
        step_id_in: Optional[list[str]] = None,
        step_name_in: Optional[list[str]] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[dict, None, None]:
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
        asset_id_in: Optional[list[str]] = None,
        issue_type: Optional[IssueType] = None,
        status: Optional[IssueStatus] = None,
        step_id_in: Optional[list[str]] = None,
        step_name_in: Optional[list[str]] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> list[dict]:
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
        asset_id_in: Optional[list[str]] = None,
        issue_type: Optional[IssueType] = None,
        status: Optional[IssueStatus] = None,
        step_id_in: Optional[list[str]] = None,
        step_name_in: Optional[list[str]] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[dict]:
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
            step_id_in: Ids of the steps the returned issues were raised in.
                Exclusive with `step_name_in`.
            step_name_in: Names of the project's current steps the returned issues were raised in.
                Only applicable if the project uses the multi-step or multi-group workflow.
                A step removed from the workflow is filtered by its id, with `step_id_in`.
                Exclusive with `step_id_in`.
            fields: All the fields to request among the possible fields for the assets.
                See [the documentation](https://api-docs.kili-technology.com/types/objects/issue) for all possible fields.
                `stepId` and `step.name` give the step an issue was raised in: null when its
                asset had finished its workflow, off a multi-step or multi-group workflow, and for
                an issue created before steps were recorded. `labelId` and `label.id` give the
                label it was raised on: null for a question, for an issue created before labels
                were recorded, and once the label is deleted.
            first: Maximum number of issues to return.
            skip: Number of issues to skip (they are ordered by their date of creation, first to last).
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the issues is returned.

        Returns:
            An iterable of issues objects represented as `dict`.

        Examples:
            >>> kili.issues(project_id=project_id, fields=['author.email']) # List all issues of a project and their authors
            >>> kili.issues(project_id=project_id, fields=['id', 'step.name', 'labelId'], step_name_in=['Review 2']) # The issues raised in the step "Review 2"
        """
        if asset_id and asset_id_in:
            raise ValueError(
                "You cannot provide both `asset_id` and `asset_id_in` at the same time."
            )

        disable_tqdm = resolve_disable_tqdm(disable_tqdm, getattr(self, "disable_tqdm", None))
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm=disable_tqdm, first=first, skip=skip)
        issues_gen = IssueUseCases(self.kili_api_gateway).list_issues(
            IssueFilters(
                project_id=ProjectId(project_id),
                asset_id=asset_id,
                asset_id_in=asset_id_in,
                issue_type=issue_type,
                status=status,
                step_id_in=_resolve_step_ids(
                    self.kili_api_gateway, project_id, step_id_in, step_name_in
                ),
            ),
            fields=fields,
            options=options,
        )
        if as_generator:
            return issues_gen
        return list(issues_gen)

    def update_issue_status(self, issue_id: str, status: IssueStatus) -> dict[str, Any]:
        """Update the status of an issue.

        Args:
            issue_id: Identifier of the issue.
            status: New status of the issue. "CANCELLED", "OPEN" or "SOLVED"

        Returns:
            A dict with the changed properties which indicates if the mutation was successful,
                else an error message.
        """
        return IssueUseCases(self.kili_api_gateway).update_issue_status(IssueId(issue_id), status)
