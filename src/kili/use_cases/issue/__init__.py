"""Issue use cases."""

from collections.abc import Generator
from typing import Any

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.issue.types import IssueToCreateKiliAPIGatewayInput
from kili.domain.issue import IssueFilters, IssueId, IssueStatus
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.use_cases.base import BaseUseCases
from kili.use_cases.issue.types import IssueToCreateUseCaseInput


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
