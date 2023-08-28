"""Issue use cases."""

from typing import List

from kili.entrypoints.mutations.issue.helpers import get_labels_asset_ids_map
from kili.gateways.kili_api_gateway import KiliAPIGateway
from kili.gateways.kili_api_gateway.issue.types import IssueToCreateKiliAPIGatewayInput
from kili.use_cases.issue.types import IssueToCreateUseCaseInput


class IssueUseCases:
    """Issue use cases."""

    def __init__(self, kili_api_gateway: KiliAPIGateway):
        self._kili_api_gateway = kili_api_gateway

    def create_issues(self, project_id, issues: List[IssueToCreateUseCaseInput]):
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
        created_issues = self._kili_api_gateway.create_issues(type_="ISSUE", issues=gateway_issues)
        return created_issues
