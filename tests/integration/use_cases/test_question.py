from kili.adapters.kili_api_gateway.issue.types import IssueToCreateKiliAPIGatewayInput
from kili.domain.asset.asset import AssetId
from kili.domain.project import ProjectId
from kili.domain.question import QuestionId
from kili.use_cases.question.question_use_case import (
    QuestionToCreateUseCaseInput,
    QuestionUseCases,
)


def test_given_text_and_asset_ids_when_calling_create_questions_it_creates_questions(
    mocker, kili_api_gateway
):
    # Given
    questions = [
        QuestionToCreateUseCaseInput(
            text="Where is the cat?",
            asset_id="fake_asset_id_1",
            asset_external_id=None,
        ),
        QuestionToCreateUseCaseInput(
            text="Where is the dog?",
            asset_id="fake_asset_id_2",
            asset_external_id=None,
        ),
    ]

    kili_api_gateway.create_issues = mocker.MagicMock(
        return_value=[QuestionId("1"), QuestionId("2")]
    )
    project_id = ProjectId("fake_project_id")

    # When
    question_ids = QuestionUseCases(kili_api_gateway).create_questions(
        project_id=project_id, questions=questions
    )

    # Then
    assert len(question_ids) == 2
    kili_api_gateway.create_issues.assert_called_once_with(
        type_="QUESTION",
        issues=[
            IssueToCreateKiliAPIGatewayInput(
                label_id=None,
                object_mid=None,
                asset_id=AssetId("fake_asset_id_1"),
                text="Where is the cat?",
            ),
            IssueToCreateKiliAPIGatewayInput(
                label_id=None,
                object_mid=None,
                asset_id=AssetId("fake_asset_id_2"),
                text="Where is the dog?",
            ),
        ],
        description="Creating questions",
    )


def test_given_text_and_external_ids_when_calling_create_questions_it_creates_questions(
    mocker, kili_api_gateway
):
    # Given
    # Given
    questions = [
        QuestionToCreateUseCaseInput(
            text="Where is the cat?",
            asset_id=None,
            asset_external_id="fake_asset_external_id_1",
        ),
        QuestionToCreateUseCaseInput(
            text="Where is the dog?",
            asset_id=None,
            asset_external_id="fake_asset_external_id_2",
        ),
    ]

    kili_api_gateway.create_issues = mocker.MagicMock(
        return_value=[QuestionId("1"), QuestionId("2")]
    )
    project_id = ProjectId("fake_project_id")

    kili_api_gateway.list_assets = mocker.MagicMock(
        return_value=[
            {"id": "fake_asset_id_1", "externalId": "fake_asset_external_id_1"},
            {"id": "fake_asset_id_2", "externalId": "fake_asset_external_id_2"},
        ]
    )

    # When
    question_ids = QuestionUseCases(kili_api_gateway).create_questions(
        project_id=project_id, questions=questions
    )

    # Then
    assert len(question_ids) == 2
    kili_api_gateway.create_issues.assert_called_once_with(
        type_="QUESTION",
        issues=[
            IssueToCreateKiliAPIGatewayInput(
                label_id=None,
                object_mid=None,
                asset_id=AssetId("fake_asset_id_1"),
                text="Where is the cat?",
            ),
            IssueToCreateKiliAPIGatewayInput(
                label_id=None,
                object_mid=None,
                asset_id=AssetId("fake_asset_id_2"),
                text="Where is the dog?",
            ),
        ],
        description="Creating questions",
    )
