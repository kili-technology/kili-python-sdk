"""Issues domain namespace for the Kili Python SDK.

This module provides a comprehensive interface for issue-related operations
including creation, querying, status management, and lifecycle operations.
"""

from itertools import repeat
from typing import Generator, List, Literal, Optional, Union, overload

from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.issue import IssueFilters, IssueId, IssueStatus, IssueType
from kili.domain.label import LabelId
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.domain_v2.issue import IssueView, validate_issue
from kili.domain_v2.project import IdListResponse, StatusResponse
from kili.presentation.client.helpers.common_validators import (
    assert_all_arrays_have_same_size,
    disable_tqdm_if_as_generator,
)
from kili.use_cases.issue import IssueUseCases
from kili.use_cases.issue.types import IssueToCreateUseCaseInput


class IssuesNamespace(DomainNamespace):
    """Issues domain namespace providing issue-related operations.

    This namespace provides access to all issue-related functionality
    including creating, updating, querying, and managing issues.

    The namespace provides the following main operations:
    - list(): Query and list issues
    - count(): Count issues matching filters
    - create(): Create new issues
    - cancel(): Cancel issues (set status to CANCELLED)
    - open(): Open issues (set status to OPEN)
    - solve(): Solve issues (set status to SOLVED)

    Examples:
        >>> kili = Kili()
        >>> # List issues
        >>> issues = kili.issues.list(project_id="my_project")

        >>> # Count issues
        >>> count = kili.issues.count(project_id="my_project")

        >>> # Create issues
        >>> result = kili.issues.create(
        ...     project_id="my_project",
        ...     label_id_array=["label_123"]
        ... )

        >>> # Solve issues
        >>> kili.issues.solve(issue_ids=["issue_123"])

        >>> # Cancel issues
        >>> kili.issues.cancel(issue_ids=["issue_456"])
    """

    def __init__(self, client, gateway):
        """Initialize the issues namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations
        """
        super().__init__(client, gateway, "issues")

    @overload
    def list(
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
    ) -> Generator[IssueView, None, None]:
        ...

    @overload
    def list(
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
    ) -> List[IssueView]:
        ...

    @typechecked
    def list(
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
    ) -> Union[Generator[IssueView, None, None], List[IssueView]]:
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
                See [the documentation](https://api-docs.kili-technology.com/types/objects/issue)
                for all possible fields.
            first: Maximum number of issues to return.
            skip: Number of issues to skip (they are ordered by their date of creation, first to last).
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the issues is returned.

        Returns:
            An iterable of IssueView objects.

        Raises:
            ValueError: If both `asset_id` and `asset_id_in` are provided.

        Examples:
            >>> # List all issues in a project
            >>> issues = kili.issues.list(project_id="my_project")

            >>> # List issues for specific assets with author info
            >>> issues = kili.issues.list(
            ...     project_id="my_project",
            ...     asset_id_in=["asset_1", "asset_2"],
            ...     fields=["id", "status", "author.email"],
            ...     as_generator=False
            ... )

            >>> # List only open issues
            >>> open_issues = kili.issues.list(
            ...     project_id="my_project",
            ...     status="OPEN",
            ...     as_generator=False
            ... )
        """
        if asset_id and asset_id_in:
            raise ValueError(
                "You cannot provide both `asset_id` and `asset_id_in` at the same time."
            )

        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm=disable_tqdm, first=first, skip=skip)

        filters = IssueFilters(
            project_id=ProjectId(project_id),
            asset_id=asset_id,
            asset_id_in=asset_id_in,
            issue_type=issue_type,
            status=status,
        )

        issue_use_cases = IssueUseCases(self.gateway)
        issues_gen = issue_use_cases.list_issues(filters=filters, fields=fields, options=options)

        # Wrap each issue dict with IssueView
        issues_view_gen = (IssueView(validate_issue(issue)) for issue in issues_gen)

        if as_generator:
            return issues_view_gen
        return list(issues_view_gen)

    @typechecked
    def count(
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

        Raises:
            ValueError: If both `asset_id` and `asset_id_in` are provided.

        Examples:
            >>> # Count all issues in a project
            >>> count = kili.issues.count(project_id="my_project")

            >>> # Count open issues for specific assets
            >>> count = kili.issues.count(
            ...     project_id="my_project",
            ...     asset_id_in=["asset_1", "asset_2"],
            ...     status="OPEN"
            ... )
        """
        if asset_id and asset_id_in:
            raise ValueError(
                "You cannot provide both `asset_id` and `asset_id_in` at the same time."
            )

        filters = IssueFilters(
            project_id=ProjectId(project_id),
            asset_id=asset_id,
            asset_id_in=asset_id_in,
            issue_type=issue_type,
            status=status,
        )

        issue_use_cases = IssueUseCases(self.gateway)
        return issue_use_cases.count_issues(filters)

    @typechecked
    def create(
        self,
        project_id: str,
        label_id_array: List[str],
        object_mid_array: Optional[List[Optional[str]]] = None,
        text_array: Optional[List[Optional[str]]] = None,
    ) -> IdListResponse:
        """Create issues for the specified labels.

        Args:
            project_id: Id of the project.
            label_id_array: List of Ids of the labels to add an issue to.
            object_mid_array: List of mids of the objects in the labels to associate the issues to.
            text_array: List of texts to associate to the issues.

        Returns:
            IdListResponse object containing the created issue IDs.
            Access the IDs with `.ids` property.

        Raises:
            ValueError: If the input arrays have different sizes.

        Examples:
            >>> # Create issues for labels
            >>> result = kili.issues.create(
            ...     project_id="my_project",
            ...     label_id_array=["label_123", "label_456"],
            ...     text_array=["Issue with annotation", "Quality concern"]
            ... )
            >>> print(result.ids)  # ['issue_1', 'issue_2']

            >>> # Create issues with object associations
            >>> result = kili.issues.create(
            ...     project_id="my_project",
            ...     label_id_array=["label_123"],
            ...     object_mid_array=["obj_mid_789"],
            ...     text_array=["Object-specific issue"]
            ... )
            >>> issue_ids = result.ids  # Access created issue IDs
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

        issue_use_cases = IssueUseCases(self.gateway)
        issue_ids = issue_use_cases.create_issues(project_id=ProjectId(project_id), issues=issues)
        results = [{"id": issue_id} for issue_id in issue_ids]
        return IdListResponse(results)

    @typechecked
    def cancel(self, issue_ids: List[str]) -> List[StatusResponse]:
        """Cancel issues by setting their status to CANCELLED.

        This method provides a more intuitive interface than the generic `update_issue_status`
        method by specifically handling the cancellation of issues with proper status transition
        validation.

        Args:
            issue_ids: List of issue IDs to cancel.

        Returns:
            List of StatusResponse objects containing the results of the status updates.
            Each response has `.id`, `.status`, `.success`, and `.error` properties.

        Raises:
            ValueError: If any issue ID is invalid or status transition is not allowed.

        Examples:
            >>> # Cancel single issue
            >>> results = kili.issues.cancel(issue_ids=["issue_123"])
            >>> for result in results:
            ...     print(f"Issue {result.id}: {'success' if result.success else result.error}")

            >>> # Cancel multiple issues
            >>> results = kili.issues.cancel(
            ...     issue_ids=["issue_123", "issue_456", "issue_789"]
            ... )
            >>> successful = [r.id for r in results if r.success]
            >>> failed = [r.id for r in results if not r.success]
        """
        issue_use_cases = IssueUseCases(self.gateway)
        results = []

        for issue_id in issue_ids:
            try:
                result = issue_use_cases.update_issue_status(
                    issue_id=IssueId(issue_id), status="CANCELLED"
                )
                results.append({"id": issue_id, "status": "CANCELLED", "success": True, **result})
            except (ValueError, TypeError, RuntimeError) as e:
                results.append(
                    {"id": issue_id, "status": "CANCELLED", "success": False, "error": str(e)}
                )

        return [StatusResponse(r) for r in results]

    @typechecked
    def open(self, issue_ids: List[str]) -> List[StatusResponse]:
        """Open issues by setting their status to OPEN.

        This method provides a more intuitive interface than the generic `update_issue_status`
        method by specifically handling the opening/reopening of issues with proper status
        transition validation.

        Args:
            issue_ids: List of issue IDs to open.

        Returns:
            List of StatusResponse objects containing the results of the status updates.
            Each response has `.id`, `.status`, `.success`, and `.error` properties.

        Raises:
            ValueError: If any issue ID is invalid or status transition is not allowed.

        Examples:
            >>> # Open single issue
            >>> results = kili.issues.open(issue_ids=["issue_123"])
            >>> for result in results:
            ...     if result.success:
            ...         print(f"Successfully opened issue {result.id}")

            >>> # Reopen multiple issues
            >>> results = kili.issues.open(
            ...     issue_ids=["issue_123", "issue_456", "issue_789"]
            ... )
            >>> print(f"Opened {sum(1 for r in results if r.success)} issues")
        """
        issue_use_cases = IssueUseCases(self.gateway)
        results = []

        for issue_id in issue_ids:
            try:
                result = issue_use_cases.update_issue_status(
                    issue_id=IssueId(issue_id), status="OPEN"
                )
                results.append({"id": issue_id, "status": "OPEN", "success": True, **result})
            except (ValueError, TypeError, RuntimeError) as e:
                results.append(
                    {"id": issue_id, "status": "OPEN", "success": False, "error": str(e)}
                )

        return [StatusResponse(r) for r in results]

    @typechecked
    def solve(self, issue_ids: List[str]) -> List[StatusResponse]:
        """Solve issues by setting their status to SOLVED.

        This method provides a more intuitive interface than the generic `update_issue_status`
        method by specifically handling the resolution of issues with proper status transition
        validation.

        Args:
            issue_ids: List of issue IDs to solve.

        Returns:
            List of StatusResponse objects containing the results of the status updates.
            Each response has `.id`, `.status`, `.success`, and `.error` properties.

        Raises:
            ValueError: If any issue ID is invalid or status transition is not allowed.

        Examples:
            >>> # Solve single issue
            >>> results = kili.issues.solve(issue_ids=["issue_123"])
            >>> if results[0].success:
            ...     print(f"Issue {results[0].id} resolved successfully")

            >>> # Solve multiple issues
            >>> results = kili.issues.solve(
            ...     issue_ids=["issue_123", "issue_456", "issue_789"]
            ... )
            >>> errors = [(r.id, r.error) for r in results if not r.success]
            >>> if errors:
            ...     print(f"Failed to solve: {errors}")
        """
        issue_use_cases = IssueUseCases(self.gateway)
        results = []

        for issue_id in issue_ids:
            try:
                result = issue_use_cases.update_issue_status(
                    issue_id=IssueId(issue_id), status="SOLVED"
                )
                results.append({"id": issue_id, "status": "SOLVED", "success": True, **result})
            except (ValueError, TypeError, RuntimeError) as e:
                results.append(
                    {"id": issue_id, "status": "SOLVED", "success": False, "error": str(e)}
                )

        return [StatusResponse(r) for r in results]

    def _validate_status_transition(
        self, issue_id: str, current_status: IssueStatus, new_status: IssueStatus
    ) -> bool:
        """Validate if a status transition is allowed.

        This is a private method that could be used for enhanced status transition validation.
        Currently, the Kili API allows all transitions, but this method provides a foundation
        for implementing business rules around status transitions if needed in the future.

        Args:
            issue_id: ID of the issue being updated
            current_status: Current status of the issue
            new_status: Desired new status

        Returns:
            True if the transition is allowed, False otherwise
        """
        # For now, we allow all transitions as per the current API behavior
        # This method can be enhanced with specific business rules if needed
        _ = issue_id  # Unused for now but may be useful for logging

        # Valid transitions (all are currently allowed by the API)
        valid_transitions = {
            "OPEN": ["SOLVED", "CANCELLED"],
            "SOLVED": ["OPEN", "CANCELLED"],
            "CANCELLED": ["OPEN", "SOLVED"],
        }

        if current_status in valid_transitions:
            return new_status in valid_transitions[current_status] or new_status == current_status

        # If we don't know the current status, allow the transition
        return True
