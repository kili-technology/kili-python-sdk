"""Issue Service."""

from typing import List, cast

from kili.entrypoints.mutations.asset.helpers import get_asset_ids_or_throw_error
from kili.entrypoints.mutations.issue.helpers import get_labels_asset_ids_map
from kili.gateways.kili_api_gateway import KiliAPIGateway
from kili.gateways.kili_api_gateway.issue.types import IssueToCreateKiliAPIGatewayInput
from kili.services.issue.types import (
    IssueToCreateServiceInput,
    QuestionToCreateServiceInput,
)


class IssueService:
    """Issue Service."""

    def __init__(self, kili_api_gateway: KiliAPIGateway):
        self._kili_api_gateway = kili_api_gateway

    def create_issues(self, project_id, issues: List[IssueToCreateServiceInput]):
        """Create issues with issue type."""
        label_id_array = [issue.label_id for issue in issues]
        label_asset_ids_map = get_labels_asset_ids_map(
            self._kili_api_gateway, project_id, label_id_array
        )  # should be done in the backend
        gateway_issues = [
            IssueToCreateKiliAPIGatewayInput(
                issue_number=0,
                label_id=issue.label_id,
                object_mid=issue.object_mid,
                asset_id=label_asset_ids_map[issue.label_id],
                text=issue.text,
            )
            for issue in issues
        ]
        created_issues = self._kili_api_gateway.create_issues(type_="ISSUE", issues=gateway_issues)
        return created_issues

    def create_questions(self, project_id: str, questions: List[QuestionToCreateServiceInput]):
        """Create issues with question type."""
        if questions[0].asset_id is None:
            asset_id_array = get_asset_ids_or_throw_error(
                self._kili_api_gateway,
                None,
                cast(List[str], [question.asset_external_id for question in questions]),
                project_id,
            )  # should be done in the backend
            for i, question in enumerate(questions):
                question.asset_id = asset_id_array[i]
        gateway_questions = [
            IssueToCreateKiliAPIGatewayInput(
                issue_number=0,
                asset_id=cast(str, question.asset_id),
                text=question.text,
                label_id=None,
                object_mid=None,
            )
            for question in questions
        ]

        created_questions = self._kili_api_gateway.create_issues(
            type_="QUESTION", issues=gateway_questions
        )
        return created_questions
