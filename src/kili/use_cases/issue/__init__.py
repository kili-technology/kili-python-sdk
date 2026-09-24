"""Issue use cases."""

from collections.abc import Generator
from typing import Any, Optional

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.issue.types import IssueToCreateKiliAPIGatewayInput
from kili.domain.issue import IssueFilters, IssueId, IssueStatus
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.exceptions import GraphQLError
from kili.use_cases.base import BaseUseCases
from kili.use_cases.issue.types import IssueToCreateUseCaseInput
from kili.utils import tqdm


class IssueUseCases(BaseUseCases):
    """Issue use cases."""

    def create_issues(
        self, project_id: ProjectId, issues: list[IssueToCreateUseCaseInput]
    ) -> list[IssueId]:
        """Create issues with issue type."""
        gateway_issues = [
            IssueToCreateKiliAPIGatewayInput(
                asset_id=None,
                label_id=issue.label_id,
                object_mid=issue.object_mid,
                text=issue.text,
            )
            for issue in issues
        ]
        return self._kili_api_gateway.create_issues(
            project_id=project_id,
            type_="ISSUE",
            issues=gateway_issues,
            description="Creating issues",
        )

    def count_issues(self, filters: IssueFilters) -> int:
        """Count issues."""
        return self._kili_api_gateway.count_issues(filters)

    def list_issues(
        self, filters: IssueFilters, fields: ListOrTuple[str], options: QueryOptions
    ) -> Generator[dict, None, None]:
        """List issues."""
        return self._kili_api_gateway.list_issues(filters=filters, fields=fields, options=options)

    def update_issue_status(self, issue_id: IssueId, status: IssueStatus) -> dict[str, Any]:
        """Update issue status."""
        return self._kili_api_gateway.update_issue_status(issue_id=issue_id, status=status)

    def reply_to_issues(
        self, issue_ids: list[IssueId], texts: list[str], disable_tqdm: Optional[bool]
    ) -> list[dict[str, Any]]:
        """Add a comment to each issue, in order, and return the created comments."""
        if any(not text.strip() for text in texts):
            raise ValueError("The text of a reply cannot be empty.")
        created_comments: list[dict[str, Any]] = []
        with tqdm.tqdm(
            total=len(issue_ids), disable=disable_tqdm, desc="Replying to issues"
        ) as pbar:
            for issue_id, text in zip(issue_ids, texts, strict=True):
                try:
                    comment = self._kili_api_gateway.append_to_comments(
                        issue_id=issue_id, text=text
                    )
                except GraphQLError as error:
                    original = error.error[0] if isinstance(error.error, list) else error.error
                    reason = original["message"] if isinstance(original, dict) else str(original)
                    replied_ids = [created["issueId"] for created in created_comments]
                    raise GraphQLError(
                        f"Could not reply to issue {issue_id}, no comment was added to it (issues"
                        f" already replied to in this call: {replied_ids or 'none'}): {reason}",
                        context=error.context,
                    ) from error
                created_comments.append(comment)
                pbar.update(1)
        return created_comments
