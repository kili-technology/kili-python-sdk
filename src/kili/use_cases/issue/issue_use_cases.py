"""Issue use cases."""

from typing import List

from kili.adapters.kili_api_gateway.issue.types import IssueToCreateKiliAPIGatewayInput
from kili.domain.issue import IssueId
from kili.domain.project import ProjectId
from kili.use_cases.base import AbstractUseCases
from kili.use_cases.issue.types import IssueToCreateUseCaseInput


class IssueUseCases(AbstractUseCases):
    """Issue use cases."""

    def create_issues(
        self, project_id: str, issues: List[IssueToCreateUseCaseInput]
    ) -> List[IssueId]:
        """Create issues with issue type."""
        gateway_issues = [
            IssueToCreateKiliAPIGatewayInput(
                label_id=issue.label_id,
                object_mid=issue.object_mid,
                text=issue.text,
            )
            for issue in issues
        ]
        return self._kili_api_gateway.create_issues(
            project_id=ProjectId(project_id), issues=gateway_issues
        )
