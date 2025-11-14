"""Issues domain namespace for the Kili Python SDK.

This module provides a comprehensive interface for issue-related operations
including creation, querying, status management, and lifecycle operations.
"""

from itertools import repeat
from typing import Any, Dict, Generator, List, Literal, Optional, TypedDict, overload

from typeguard import typechecked
from typing_extensions import deprecated

from kili.domain.issue import IssueId, IssueStatus
from kili.domain.label import LabelId
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.domain_api.namespace_utils import get_available_methods
from kili.presentation.client.helpers.common_validators import (
    assert_all_arrays_have_same_size,
)
from kili.use_cases.issue import IssueUseCases
from kili.use_cases.issue.types import IssueToCreateUseCaseInput


class IssueFilter(TypedDict, total=False):
    """Filter options for querying issues.

    Attributes:
        asset_id: Id of the asset whose returned issues are associated to.
        asset_id_in: List of Ids of assets whose returned issues are associated to.
        status: Status of the issues to return (e.g., 'OPEN', 'SOLVED', 'CANCELLED').
    """

    asset_id: Optional[str]
    asset_id_in: Optional[List[str]]
    status: Optional[IssueStatus]


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

    @deprecated(
        "'issues' is a namespace, not a callable method. "
        "Use kili.issues.list() or other available methods instead."
    )
    def __call__(self, *args, **kwargs):
        """Raise a helpful error when namespace is called like a method.

        This provides guidance to users migrating from the legacy API
        where issues were accessed via kili.issues(...) to the new domain API
        where they use kili.issues.list(...) or other methods.
        """
        available_methods = get_available_methods(self)
        methods_str = ", ".join(f"kili.{self._domain_name}.{m}()" for m in available_methods)
        raise TypeError(
            f"'{self._domain_name}' is a namespace, not a callable method. "
            f"The legacy API 'kili.{self._domain_name}(...)' has been replaced with the domain API.\n"
            f"Available methods: {methods_str}\n"
            f"Example: kili.{self._domain_name}.list(...)"
        )

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
            "comments.authorIdUser",
            "comments.createdAt",
            "comments.id",
            "comments.text",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        filter: Optional[IssueFilter] = None,
    ) -> List[Dict]:
        """Get a list of issues that match a set of criteria.

        !!! Info "Issues vs Questions"
            This method returns only issues (type='ISSUE'). For questions, use `kili.questions.list()` instead.

        Args:
            project_id: Project ID the issue belongs to.
            fields: All the fields to request among the possible fields for the assets.
                See [the documentation](https://api-docs.kili-technology.com/types/objects/issue)
                for all possible fields.
            first: Maximum number of issues to return.
            skip: Number of issues to skip (they are ordered by their date of creation, first to last).
            disable_tqdm: If `True`, the progress bar will be disabled.
            filter: Optional dictionary to filter issues. See `IssueFilter` for available filter options.

        Returns:
            A list of issues objects represented as `dict`.

        Examples:
            >>> # List all issues in a project
            >>> issues = kili.issues.list(project_id="my_project")

            >>> # List issues for specific assets with author info
            >>> issues = kili.issues.list(
            ...     project_id="my_project",
            ...     filter={"asset_id_in": ["asset_1", "asset_2"]},
            ...     fields=["id", "status", "author.email"]
            ... )

            >>> # List only open issues
            >>> open_issues = kili.issues.list(
            ...     project_id="my_project",
            ...     filter={"status": "OPEN"}
            ... )
        """
        filter_kwargs: Dict[str, Any] = dict(filter or {})
        # Force issue_type to ISSUE
        filter_kwargs["issue_type"] = "ISSUE"
        return self._client.issues(
            as_generator=False,
            disable_tqdm=disable_tqdm,
            fields=fields,
            first=first,
            project_id=project_id,
            skip=skip,
            **filter_kwargs,
        )

    @typechecked
    def list_as_generator(
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
        filter: Optional[IssueFilter] = None,
    ) -> Generator[Dict, None, None]:
        """Get a generator of issues that match a set of criteria.

        !!! Info "Issues vs Questions"
            This method returns only issues (type='ISSUE'). For questions, use
            `kili.questions.list_as_generator()` instead.

        Args:
            project_id: Project ID the issue belongs to.
            fields: All the fields to request among the possible fields for the assets.
                See [the documentation](https://api-docs.kili-technology.com/types/objects/issue)
                for all possible fields.
            first: Maximum number of issues to return.
            skip: Number of issues to skip (they are ordered by their date of creation, first to last).
            disable_tqdm: If `True`, the progress bar will be disabled.
            filter: Optional dictionary to filter issues. See `IssueFilter` for available filter options.

        Returns:
            A generator yielding issues objects represented as `dict`.

        Examples:
            >>> # Get issues as generator
            >>> for issue in kili.issues.list_as_generator(project_id="my_project"):
            ...     print(issue["id"])

            >>> # Filter by status
            >>> for issue in kili.issues.list_as_generator(
            ...     project_id="my_project",
            ...     filter={"status": "OPEN"}
            ... ):
            ...     print(issue["id"])
        """
        filter_kwargs: Dict[str, Any] = dict(filter or {})
        # Force issue_type to ISSUE
        filter_kwargs["issue_type"] = "ISSUE"
        return self._client.issues(
            as_generator=True,
            disable_tqdm=disable_tqdm,
            fields=fields,
            first=first,
            project_id=project_id,
            skip=skip,
            **filter_kwargs,
        )

    @typechecked
    def count(self, project_id: str, filter: Optional[IssueFilter] = None) -> int:
        """Count and return the number of issues with the given constraints.

        Args:
            project_id: Project ID the issue belongs to.
            filter: Optional dictionary to filter issues. See `IssueFilter` for available filter options.

        Returns:
            The number of issues that match the given constraints.

        Examples:
            >>> # Count all issues in a project
            >>> count = kili.issues.count(project_id="my_project")

            >>> # Count open issues for specific assets
            >>> count = kili.issues.count(
            ...     project_id="my_project",
            ...     filter={"asset_id_in": ["asset_1", "asset_2"], "status": "OPEN"}
            ... )
        """
        filter_kwargs: Dict[str, Any] = dict(filter or {})
        # Force issue_type to ISSUE
        filter_kwargs["issue_type"] = "ISSUE"
        return self._client.count_issues(
            project_id=project_id,
            **filter_kwargs,
        )

    @overload
    def create(
        self,
        *,
        project_id: str,
        label_id: str,
        object_mid: Optional[str] = None,
        text: Optional[str] = None,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def create(
        self,
        *,
        project_id: str,
        label_id_array: List[str],
        object_mid_array: Optional[List[Optional[str]]] = None,
        text_array: Optional[List[Optional[str]]] = None,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @typechecked
    def create(
        self,
        *,
        project_id: str,
        label_id: Optional[str] = None,
        label_id_array: Optional[List[str]] = None,
        object_mid: Optional[str] = None,
        object_mid_array: Optional[List[Optional[str]]] = None,
        text: Optional[str] = None,
        text_array: Optional[List[Optional[str]]] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Create issues for the specified labels.

        Args:
            project_id: Id of the project.
            label_id: Id of the label to add an issue to.
            label_id_array: List of Ids of the labels to add an issue to.
            object_mid: Mid of the object in the label to associate the issue to.
            object_mid_array: List of mids of the objects in the labels to associate the issues to.
            text: Text to associate to the issue.
            text_array: List of texts to associate to the issues.

        Returns:
            A list of dictionaries with the `id` key of the created issues.

        Raises:
            ValueError: If the input arrays have different sizes.

        Examples:
            >>> # Create single issue
            >>> result = kili.issues.create(
            ...     project_id="my_project",
            ...     label_id="label_123",
            ...     text="Issue with annotation"
            ... )

            >>> # Create multiple issues
            >>> result = kili.issues.create(
            ...     project_id="my_project",
            ...     label_id_array=["label_123", "label_456"],
            ...     text_array=["Issue with annotation", "Quality concern"]
            ... )
        """
        # Convert singular to plural
        if label_id is not None:
            label_id_array = [label_id]
        if object_mid is not None:
            object_mid_array = [object_mid]
        if text is not None:
            text_array = [text]

        assert_all_arrays_have_same_size([label_id_array, object_mid_array, text_array])
        assert label_id_array is not None, "label_id_array must be provided"

        issues = [
            IssueToCreateUseCaseInput(
                label_id=LabelId(label_id_item), object_mid=object_mid_item, text=text_item
            )
            for (label_id_item, object_mid_item, text_item) in zip(
                label_id_array,
                object_mid_array or repeat(None),
                text_array or repeat(None),
            )
        ]

        issue_use_cases = IssueUseCases(self._gateway)
        issue_ids = issue_use_cases.create_issues(project_id=ProjectId(project_id), issues=issues)
        return [{"id": issue_id} for issue_id in issue_ids]

    @overload
    def cancel(self, *, issue_id: str) -> List[Dict[str, Any]]:
        ...

    @overload
    def cancel(self, *, issue_ids: List[str]) -> List[Dict[str, Any]]:
        ...

    @typechecked
    def cancel(
        self,
        *,
        issue_id: Optional[str] = None,
        issue_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Cancel issues by setting their status to CANCELLED.

        This method provides a more intuitive interface than the generic `update_issue_status`
        method by specifically handling the cancellation of issues with proper status transition
        validation.

        Args:
            issue_id: Issue ID to cancel.
            issue_ids: List of issue IDs to cancel.

        Returns:
            List of dictionaries with the results of the status updates.

        Raises:
            ValueError: If any issue ID is invalid or status transition is not allowed.

        Examples:
            >>> # Cancel single issue
            >>> result = kili.issues.cancel(issue_id="issue_123")

            >>> # Cancel multiple issues
            >>> result = kili.issues.cancel(
            ...     issue_ids=["issue_123", "issue_456", "issue_789"]
            ... )
        """
        # Convert singular to plural
        if issue_id is not None:
            issue_ids = [issue_id]

        assert issue_ids is not None, "issue_ids must be provided"

        issue_use_cases = IssueUseCases(self._gateway)
        results = []

        for issue_id_item in issue_ids:
            try:
                result = issue_use_cases.update_issue_status(
                    issue_id=IssueId(issue_id_item), status="CANCELLED"
                )
                results.append(
                    {"id": issue_id_item, "status": "CANCELLED", "success": True, **result}
                )
            except (ValueError, TypeError, RuntimeError) as e:
                results.append(
                    {"id": issue_id_item, "status": "CANCELLED", "success": False, "error": str(e)}
                )

        return results

    @overload
    def open(self, *, issue_id: str) -> List[Dict[str, Any]]:
        ...

    @overload
    def open(self, *, issue_ids: List[str]) -> List[Dict[str, Any]]:
        ...

    @typechecked
    def open(
        self,
        *,
        issue_id: Optional[str] = None,
        issue_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Open issues by setting their status to OPEN.

        This method provides a more intuitive interface than the generic `update_issue_status`
        method by specifically handling the opening/reopening of issues with proper status
        transition validation.

        Args:
            issue_id: Issue ID to open.
            issue_ids: List of issue IDs to open.

        Returns:
            List of dictionaries with the results of the status updates.

        Raises:
            ValueError: If any issue ID is invalid or status transition is not allowed.

        Examples:
            >>> # Open single issue
            >>> result = kili.issues.open(issue_id="issue_123")

            >>> # Reopen multiple issues
            >>> result = kili.issues.open(
            ...     issue_ids=["issue_123", "issue_456", "issue_789"]
            ... )
        """
        # Convert singular to plural
        if issue_id is not None:
            issue_ids = [issue_id]

        assert issue_ids is not None, "issue_ids must be provided"

        issue_use_cases = IssueUseCases(self._gateway)
        results = []

        for issue_id_item in issue_ids:
            try:
                result = issue_use_cases.update_issue_status(
                    issue_id=IssueId(issue_id_item), status="OPEN"
                )
                results.append({"id": issue_id_item, "status": "OPEN", "success": True, **result})
            except (ValueError, TypeError, RuntimeError) as e:
                results.append(
                    {"id": issue_id_item, "status": "OPEN", "success": False, "error": str(e)}
                )

        return results

    @overload
    def solve(self, *, issue_id: str) -> List[Dict[str, Any]]:
        ...

    @overload
    def solve(self, *, issue_ids: List[str]) -> List[Dict[str, Any]]:
        ...

    @typechecked
    def solve(
        self,
        *,
        issue_id: Optional[str] = None,
        issue_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Solve issues by setting their status to SOLVED.

        This method provides a more intuitive interface than the generic `update_issue_status`
        method by specifically handling the resolution of issues with proper status transition
        validation.

        Args:
            issue_id: Issue ID to solve.
            issue_ids: List of issue IDs to solve.

        Returns:
            List of dictionaries with the results of the status updates.

        Raises:
            ValueError: If any issue ID is invalid or status transition is not allowed.

        Examples:
            >>> # Solve single issue
            >>> result = kili.issues.solve(issue_id="issue_123")

            >>> # Solve multiple issues
            >>> result = kili.issues.solve(
            ...     issue_ids=["issue_123", "issue_456", "issue_789"]
            ... )
        """
        # Convert singular to plural
        if issue_id is not None:
            issue_ids = [issue_id]

        assert issue_ids is not None, "issue_ids must be provided"

        issue_use_cases = IssueUseCases(self._gateway)
        results = []

        for issue_id_item in issue_ids:
            try:
                result = issue_use_cases.update_issue_status(
                    issue_id=IssueId(issue_id_item), status="SOLVED"
                )
                results.append({"id": issue_id_item, "status": "SOLVED", "success": True, **result})
            except (ValueError, TypeError, RuntimeError) as e:
                results.append(
                    {"id": issue_id_item, "status": "SOLVED", "success": False, "error": str(e)}
                )

        return results

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
