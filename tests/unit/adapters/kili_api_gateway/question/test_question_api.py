from typing import Dict, List

import pytest

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.issue.operations import GQL_CREATE_ISSUES
from kili.adapters.kili_api_gateway.question import QuestionOperationMixin
from kili.adapters.kili_api_gateway.question.types import QuestionsToCreateGatewayInput
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.asset import AssetExternalId, AssetId
from kili.domain.project import ProjectId


@pytest.mark.parametrize(
    "questions, expected_payload",
    (
        (
            [
                QuestionsToCreateGatewayInput(
                    asset_id=AssetId("asset_id"),
                    text="text",
                )
            ],
            {
                "issues": [
                    {
                        "issueNumber": 0,
                        "type": "QUESTION",
                        "assetId": "asset_id",
                        "text": "text",
                    }
                ],
                "where": {"idIn": ["asset_id"]},
            },
        ),
        (
            [
                QuestionsToCreateGatewayInput(
                    external_id=AssetExternalId("asset_external_id"),
                    text="text",
                )
            ],
            {
                "issues": [
                    {
                        "issueNumber": 0,
                        "type": "QUESTION",
                        "assetId": "asset_id",
                        "text": "text",
                    }
                ],
                "where": {"idIn": ["asset_id"]},
            },
        ),
    ),
)
def test_creates_a_question_from_asset_id(
    questions: List[QuestionsToCreateGatewayInput],
    expected_payload: Dict,
    mocker,
    mocked_graphql_client: GraphQLClient,
    mocked_http_client: HttpClient,
):
    # Given
    question_operations = QuestionOperationMixin()
    question_operations.graphql_client = mocked_graphql_client
    question_operations.http_client = mocked_http_client
    mocker.patch(
        "kili.adapters.kili_api_gateway.base.BaseOperationMixin._get_asset_ids_or_throw_error",
        return_value=[AssetId("asset_id")],
    )

    # When
    question_operations.create_questions(
        project_id=ProjectId("project_id"), questions=questions, disable_tqdm=False
    )

    # Then
    question_operations.graphql_client.execute.assert_called_with(
        GQL_CREATE_ISSUES, expected_payload
    )
