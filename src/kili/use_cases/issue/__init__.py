"""Issue use cases."""

from typing import Dict, Generator, List

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.issue.types import IssueToCreateKiliAPIGatewayInput
from kili.domain.issue import IssueFilters, IssueId
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.entrypoints.mutations.issue.helpers import get_labels_asset_ids_map
from kili.use_cases.base import BaseUseCases
from kili.use_cases.issue.types import IssueToCreateUseCaseInput


class IssueUseCases(BaseUseCases):
    """Issue use cases."""

    def create_issues(
        self, project_id: ProjectId, issues: List[IssueToCreateUseCaseInput]
    ) -> List[IssueId]:
        """Create issues with issue type."""
        label_id_array = [issue.label_id for issue in issues]
        label_asset_ids_map = get_labels_asset_ids_map(
            self._kili_api_gateway, project_id, label_id_array
        )  # TODO: should be done in the backend
        gateway_issues = [
            IssueToCreateKiliAPIGatewayInput(
                label_id=issue.label_id,
                object_mid=issue.object_mid,
                asset_id=label_asset_ids_map[issue.label_id],
                text=issue.text,
            )
            for issue in issues
        ]
        return self._kili_api_gateway.create_issues(
            type_="ISSUE", issues=gateway_issues, description="Creating issues"
        )

    def count_issues(self, filters: IssueFilters) -> int:
        """Count issues."""
        return self._kili_api_gateway.count_issues(filters)

    def list_issues(
        self, filters: IssueFilters, fields: ListOrTuple[str], options: QueryOptions
    ) -> Generator[Dict, None, None]:
        """List issues."""
        return self._kili_api_gateway.list_issues(filters=filters, fields=fields, options=options)
