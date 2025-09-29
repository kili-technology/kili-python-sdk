"""Questions domain namespace for the Kili Python SDK.

This module provides a comprehensive interface for question-related operations
including creation, querying, status management, and lifecycle operations.
"""

from itertools import repeat
from typing import Any, Dict, Generator, List, Literal, Optional, TypedDict, overload

from typeguard import typechecked
from typing_extensions import deprecated

from kili.domain.asset import AssetExternalId, AssetId
from kili.domain.issue import IssueId, IssueStatus
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.domain_api.namespace_utils import get_available_methods
from kili.presentation.client.helpers.common_validators import (
    assert_all_arrays_have_same_size,
)
from kili.use_cases.issue import IssueUseCases
from kili.use_cases.question import QuestionToCreateUseCaseInput, QuestionUseCases


class QuestionFilter(TypedDict, total=False):
    """Filter options for querying questions.

    Attributes:
        asset_id: Id of the asset whose returned questions are associated to.
        asset_id_in: List of Ids of assets whose returned questions are associated to.
        status: Status of the questions to return (e.g., 'OPEN', 'SOLVED', 'CANCELLED').
    """

    asset_id: Optional[str]
    asset_id_in: Optional[List[str]]
    status: Optional[IssueStatus]


class QuestionsNamespace(DomainNamespace):
    """Questions domain namespace providing question-related operations.

    This namespace provides access to all question-related functionality
    including creating, updating, querying, and managing questions.

    The namespace provides the following main operations:
    - list(): Query and list questions
    - count(): Count questions matching filters
    - create(): Create new questions
    - cancel(): Cancel questions (set status to CANCELLED)
    - open(): Open questions (set status to OPEN)
    - solve(): Solve questions (set status to SOLVED)

    Examples:
        >>> kili = Kili()
        >>> # List questions
        >>> questions = kili.questions.list(project_id="my_project")

        >>> # Count questions
        >>> count = kili.questions.count(project_id="my_project")

        >>> # Create questions
        >>> result = kili.questions.create(
        ...     project_id="my_project",
        ...     asset_id_array=["asset_123"],
        ...     text_array=["What is the classification?"]
        ... )

        >>> # Solve questions
        >>> kili.questions.solve(question_ids=["question_123"])

        >>> # Cancel questions
        >>> kili.questions.cancel(question_ids=["question_456"])
    """

    def __init__(self, client, gateway):
        """Initialize the questions namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations
        """
        super().__init__(client, gateway, "questions")

    @deprecated(
        "'questions' is a namespace, not a callable method. "
        "Use kili.questions.list() or other available methods instead."
    )
    def __call__(self, *args, **kwargs):
        """Raise a helpful error when namespace is called like a method.

        This provides guidance to users migrating from the legacy API
        where questions were accessed via kili.questions(...) to the new domain API
        where they use kili.questions.list(...) or other methods.
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
        filter: Optional[QuestionFilter] = None,
    ) -> List[Dict]:
        """Get a list of questions that match a set of criteria.

        Args:
            project_id: Project ID the question belongs to.
            fields: All the fields to request among the possible fields for the questions.
                See [the documentation](https://api-docs.kili-technology.com/types/objects/issue)
                for all possible fields.
            first: Maximum number of questions to return.
            skip: Number of questions to skip (they are ordered by their date of creation, first to last).
            disable_tqdm: If `True`, the progress bar will be disabled.
            filter: Optional dictionary to filter questions. See `QuestionFilter` for available filter options.

        Returns:
            A list of question objects represented as `dict`.

        Examples:
            >>> # List all questions in a project
            >>> questions = kili.questions.list(project_id="my_project")

            >>> # List questions for specific assets with author info
            >>> questions = kili.questions.list(
            ...     project_id="my_project",
            ...     filter={"asset_id_in": ["asset_1", "asset_2"]},
            ...     fields=["id", "status", "author.email"]
            ... )

            >>> # List only open questions
            >>> open_questions = kili.questions.list(
            ...     project_id="my_project",
            ...     filter={"status": "OPEN"}
            ... )
        """
        filter_kwargs: Dict[str, Any] = dict(filter or {})
        # Force issue_type to QUESTION
        filter_kwargs["issue_type"] = "QUESTION"
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
        filter: Optional[QuestionFilter] = None,
    ) -> Generator[Dict, None, None]:
        """Get a generator of questions that match a set of criteria.

        Args:
            project_id: Project ID the question belongs to.
            fields: All the fields to request among the possible fields for the questions.
                See [the documentation](https://api-docs.kili-technology.com/types/objects/issue)
                for all possible fields.
            first: Maximum number of questions to return.
            skip: Number of questions to skip (they are ordered by their date of creation, first to last).
            disable_tqdm: If `True`, the progress bar will be disabled.
            filter: Optional dictionary to filter questions. See `QuestionFilter` for available filter options.

        Returns:
            A generator yielding question objects represented as `dict`.

        Examples:
            >>> # Get questions as generator
            >>> for question in kili.questions.list_as_generator(project_id="my_project"):
            ...     print(question["id"])

            >>> # Filter by status
            >>> for question in kili.questions.list_as_generator(
            ...     project_id="my_project",
            ...     filter={"status": "OPEN"}
            ... ):
            ...     print(question["id"])
        """
        filter_kwargs: Dict[str, Any] = dict(filter or {})
        # Force issue_type to QUESTION
        filter_kwargs["issue_type"] = "QUESTION"
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
    def count(self, project_id: str, filter: Optional[QuestionFilter] = None) -> int:
        """Count and return the number of questions with the given constraints.

        Args:
            project_id: Project ID the question belongs to.
            filter: Optional dictionary to filter questions. See `QuestionFilter` for available filter options.

        Returns:
            The number of questions that match the given constraints.

        Examples:
            >>> # Count all questions in a project
            >>> count = kili.questions.count(project_id="my_project")

            >>> # Count open questions for specific assets
            >>> count = kili.questions.count(
            ...     project_id="my_project",
            ...     filter={"asset_id_in": ["asset_1", "asset_2"], "status": "OPEN"}
            ... )
        """
        filter_kwargs: Dict[str, Any] = dict(filter or {})
        # Force issue_type to QUESTION
        filter_kwargs["issue_type"] = "QUESTION"
        return self._client.count_issues(
            project_id=project_id,
            **filter_kwargs,
        )

    @overload
    def create(
        self,
        *,
        project_id: str,
        asset_id: str,
        text: Optional[str] = None,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def create(
        self,
        *,
        project_id: str,
        asset_external_id: str,
        text: Optional[str] = None,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def create(
        self,
        *,
        project_id: str,
        asset_id_array: List[str],
        text_array: Optional[List[Optional[str]]] = None,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def create(
        self,
        *,
        project_id: str,
        asset_external_id_array: List[str],
        text_array: Optional[List[Optional[str]]] = None,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @typechecked
    def create(
        self,
        *,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_id_array: Optional[List[str]] = None,
        asset_external_id: Optional[str] = None,
        asset_external_id_array: Optional[List[str]] = None,
        text: Optional[str] = None,
        text_array: Optional[List[Optional[str]]] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Create questions for the specified assets.

        Args:
            project_id: Id of the project.
            asset_id: Id of the asset to add a question to.
            asset_id_array: List of Ids of the assets to add questions to.
            asset_external_id: External id of the asset to add a question to.
            asset_external_id_array: List of external ids of the assets to add questions to.
            text: Text to associate to the question.
            text_array: List of texts to associate to the questions.

        Returns:
            A list of dictionaries with the `id` key of the created questions.

        Raises:
            ValueError: If the input arrays have different sizes.

        Examples:
            >>> # Create single question by asset ID
            >>> result = kili.questions.create(
            ...     project_id="my_project",
            ...     asset_id="asset_123",
            ...     text="What is the classification?"
            ... )

            >>> # Create single question by external ID
            >>> result = kili.questions.create(
            ...     project_id="my_project",
            ...     asset_external_id="my_asset_001",
            ...     text="Is this correct?"
            ... )

            >>> # Create multiple questions
            >>> result = kili.questions.create(
            ...     project_id="my_project",
            ...     asset_id_array=["asset_123", "asset_456"],
            ...     text_array=["Question 1", "Question 2"]
            ... )
        """
        # Convert singular to plural
        if asset_id is not None:
            asset_id_array = [asset_id]
        if asset_external_id is not None:
            asset_external_id_array = [asset_external_id]
        if text is not None:
            text_array = [text]

        assert_all_arrays_have_same_size([asset_id_array, asset_external_id_array, text_array])
        assert (
            asset_id_array is not None or asset_external_id_array is not None
        ), "Either asset_id_array or asset_external_id_array must be provided"

        questions = [
            QuestionToCreateUseCaseInput(
                text=text_item,
                asset_id=AssetId(asset_id_item) if asset_id_item else None,
                asset_external_id=(
                    AssetExternalId(asset_external_id_item) if asset_external_id_item else None
                ),
            )
            for (text_item, asset_id_item, asset_external_id_item) in zip(
                text_array or repeat(None),
                asset_id_array or repeat(None),
                asset_external_id_array or repeat(None),
            )
        ]

        question_use_cases = QuestionUseCases(self._gateway)
        question_ids = question_use_cases.create_questions(
            project_id=ProjectId(project_id), questions=questions
        )
        return [{"id": question_id} for question_id in question_ids]

    @overload
    def cancel(self, *, question_id: str) -> List[Dict[str, Any]]:
        ...

    @overload
    def cancel(self, *, question_ids: List[str]) -> List[Dict[str, Any]]:
        ...

    @typechecked
    def cancel(
        self,
        *,
        question_id: Optional[str] = None,
        question_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Cancel questions by setting their status to CANCELLED.

        This method provides a more intuitive interface than the generic `update_issue_status`
        method by specifically handling the cancellation of questions with proper status transition
        validation.

        Args:
            question_id: Question ID to cancel.
            question_ids: List of question IDs to cancel.

        Returns:
            List of dictionaries with the results of the status updates.

        Raises:
            ValueError: If any question ID is invalid or status transition is not allowed.

        Examples:
            >>> # Cancel single question
            >>> result = kili.questions.cancel(question_id="question_123")

            >>> # Cancel multiple questions
            >>> result = kili.questions.cancel(
            ...     question_ids=["question_123", "question_456", "question_789"]
            ... )
        """
        # Convert singular to plural
        if question_id is not None:
            question_ids = [question_id]

        assert question_ids is not None, "question_ids must be provided"

        issue_use_cases = IssueUseCases(self._gateway)
        results = []

        for question_id_item in question_ids:
            try:
                result = issue_use_cases.update_issue_status(
                    issue_id=IssueId(question_id_item), status="CANCELLED"
                )
                results.append(
                    {"id": question_id_item, "status": "CANCELLED", "success": True, **result}
                )
            except (ValueError, TypeError, RuntimeError) as e:
                results.append(
                    {
                        "id": question_id_item,
                        "status": "CANCELLED",
                        "success": False,
                        "error": str(e),
                    }
                )

        return results

    @overload
    def open(self, *, question_id: str) -> List[Dict[str, Any]]:
        ...

    @overload
    def open(self, *, question_ids: List[str]) -> List[Dict[str, Any]]:
        ...

    @typechecked
    def open(
        self,
        *,
        question_id: Optional[str] = None,
        question_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Open questions by setting their status to OPEN.

        This method provides a more intuitive interface than the generic `update_issue_status`
        method by specifically handling the opening/reopening of questions with proper status
        transition validation.

        Args:
            question_id: Question ID to open.
            question_ids: List of question IDs to open.

        Returns:
            List of dictionaries with the results of the status updates.

        Raises:
            ValueError: If any question ID is invalid or status transition is not allowed.

        Examples:
            >>> # Open single question
            >>> result = kili.questions.open(question_id="question_123")

            >>> # Reopen multiple questions
            >>> result = kili.questions.open(
            ...     question_ids=["question_123", "question_456", "question_789"]
            ... )
        """
        # Convert singular to plural
        if question_id is not None:
            question_ids = [question_id]

        assert question_ids is not None, "question_ids must be provided"

        issue_use_cases = IssueUseCases(self._gateway)
        results = []

        for question_id_item in question_ids:
            try:
                result = issue_use_cases.update_issue_status(
                    issue_id=IssueId(question_id_item), status="OPEN"
                )
                results.append(
                    {"id": question_id_item, "status": "OPEN", "success": True, **result}
                )
            except (ValueError, TypeError, RuntimeError) as e:
                results.append(
                    {"id": question_id_item, "status": "OPEN", "success": False, "error": str(e)}
                )

        return results

    @overload
    def solve(self, *, question_id: str) -> List[Dict[str, Any]]:
        ...

    @overload
    def solve(self, *, question_ids: List[str]) -> List[Dict[str, Any]]:
        ...

    @typechecked
    def solve(
        self,
        *,
        question_id: Optional[str] = None,
        question_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Solve questions by setting their status to SOLVED.

        This method provides a more intuitive interface than the generic `update_issue_status`
        method by specifically handling the resolution of questions with proper status transition
        validation.

        Args:
            question_id: Question ID to solve.
            question_ids: List of question IDs to solve.

        Returns:
            List of dictionaries with the results of the status updates.

        Raises:
            ValueError: If any question ID is invalid or status transition is not allowed.

        Examples:
            >>> # Solve single question
            >>> result = kili.questions.solve(question_id="question_123")

            >>> # Solve multiple questions
            >>> result = kili.questions.solve(
            ...     question_ids=["question_123", "question_456", "question_789"]
            ... )
        """
        # Convert singular to plural
        if question_id is not None:
            question_ids = [question_id]

        assert question_ids is not None, "question_ids must be provided"

        issue_use_cases = IssueUseCases(self._gateway)
        results = []

        for question_id_item in question_ids:
            try:
                result = issue_use_cases.update_issue_status(
                    issue_id=IssueId(question_id_item), status="SOLVED"
                )
                results.append(
                    {"id": question_id_item, "status": "SOLVED", "success": True, **result}
                )
            except (ValueError, TypeError, RuntimeError) as e:
                results.append(
                    {"id": question_id_item, "status": "SOLVED", "success": False, "error": str(e)}
                )

        return results
