from typing import List, Optional

from kili.core.graphql.graphql_gateway import GraphQLGateway
from kili.core.graphql.operations.issue.types import IssueToCreateGraphQLGatewayInput
from kili.entrypoints.mutations.asset.helpers import get_asset_ids_or_throw_error
from kili.entrypoints.mutations.issue.helpers import (
    get_issue_numbers,
    get_labels_asset_ids_map,
)
from kili.services.issues.types import IssueToCreateEntrypointInput


class IssueUseCases:
    def __init__(self, graphql_gateway: GraphQLGateway):
        self._graphql_gateway = graphql_gateway

    def create_issues(self, project_id, issues: List[IssueToCreateEntrypointInput]):
        issue_number_array = get_issue_numbers(
            self._graphql_gateway, project_id, "ISSUE", len(issues)
        )
        label_id_array = [issue.label_id for issue in issues]
        label_asset_ids_map = get_labels_asset_ids_map(
            self._graphql_gateway, project_id, label_id_array
        )  # should be done in the backend
        graphql_issues = [
            IssueToCreateGraphQLGatewayInput(
                issue_number=issue_number,
                label_id=issue.label_id,
                object_mid=issue.object_mid,
                asset_id=label_asset_ids_map[issue.label_id],
                text=issue.text,
            )
            for (issue_number, issue) in zip(issue_number_array, issues)
        ]
        issue_ids = self._graphql_gateway.create_issues(type_="ISSUE", issues=graphql_issues)
        return issue_ids

    def create_questions(
        self,
        project_id: str,
        text_array: List[str],
        asset_id_array: Optional[List[str]],
        asset_external_id_array: Optional[List[str]],
    ):
        issue_number_array = get_issue_numbers(self, project_id, "QUESTION", len(text_array))
        asset_id_array = get_asset_ids_or_throw_error(
            self._graphql_gateway, asset_id_array, asset_external_id_array, project_id
        )  # should be done in the backend
        graphql_questions = [
            IssueToCreateGraphQLGatewayInput(
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

        issue_ids = self._graphql_gateway.create_issues(type_="QUESTION", issues=graphql_questions)
        return issue_ids
