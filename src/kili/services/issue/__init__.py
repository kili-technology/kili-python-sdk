"""Issue Service."""

from typing import List, Optional

from kili.core.graphql.gateway import GraphQLGateway
from kili.core.graphql.gateway.issue.types import IssueToCreateGQLGatewayInput
from kili.entrypoints.mutations.asset.helpers import get_asset_ids_or_throw_error
from kili.entrypoints.mutations.issue.helpers import get_labels_asset_ids_map
from kili.services.issue.types import IssueToCreateServiceInput


class IssueService:
    """Issue Service."""

    def __init__(self, graphql_gateway: GraphQLGateway):
        self._graphql_gateway = graphql_gateway

    def create_issues(self, project_id, issues: List[IssueToCreateServiceInput]):
        """Create issues with issue type."""
        issue_number_array = [0] * len(issues)
        label_id_array = [issue.label_id for issue in issues]
        label_asset_ids_map = get_labels_asset_ids_map(
            self._graphql_gateway, project_id, label_id_array
        )  # should be done in the backend
        graphql_issues = [
            IssueToCreateGQLGatewayInput(
                issue_number=issue_number,
                label_id=issue.label_id,
                object_mid=issue.object_mid,
                asset_id=label_asset_ids_map[issue.label_id],
                text=issue.text,
            )
            for (issue_number, issue) in zip(issue_number_array, issues)
        ]
        created_issues = self._graphql_gateway.create_issues(type_="ISSUE", issues=graphql_issues)
        return created_issues

    def create_questions(
        self,
        project_id: str,
        text_array: List[str],
        asset_id_array: Optional[List[str]],
        asset_external_id_array: Optional[List[str]],
    ):
        """Create issues with question type."""
        issue_number_array = [0] * len(text_array)
        asset_id_array = get_asset_ids_or_throw_error(
            self._graphql_gateway, asset_id_array, asset_external_id_array, project_id
        )  # should be done in the backend
        graphql_questions = [
            IssueToCreateGQLGatewayInput(
                issue_number=issue_number,
                asset_id=asset_id,
                text=text,
                label_id=None,
                object_mid=None,
            )
            for (issue_number, asset_id, text) in zip(
                issue_number_array, asset_id_array, text_array
            )
        ]

        created_questions = self._graphql_gateway.create_issues(
            type_="QUESTION", issues=graphql_questions
        )
        return created_questions
