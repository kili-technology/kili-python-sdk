from typing import List, Optional, cast

import pytest_mock

from kili.adapters.kili_api_gateway.mixin import KiliAPIGateway
from kili.domain.asset.asset import AssetId
from kili.domain.project import ProjectId
from kili.domain.question import QuestionId
from kili.presentation.client.question import QuestionClientMethods
from kili.use_cases.question.question_use_case import QuestionToCreateUseCaseInput


def test_given_text_and_asset_ids_when_calling_create_questions_it_creates_questions(
    mocker: pytest_mock.MockerFixture, kili_api_gateway: KiliAPIGateway
):
    # Given
    questions = cast(List[Optional[str]], ["Where is the cat?", "Where is the dog?"])
    kili = QuestionClientMethods()
    kili.kili_api_gateway = kili_api_gateway
    project_id = "fake_project_id"
    asset_id_array = ["fake_asset_id_1", "fake_asset_id_2"]
    mock_question_use_case_create_questions = mocker.patch(
        "kili.presentation.client.question.QuestionUseCases.create_questions",
        return_value=[QuestionId("1"), QuestionId("2")],
    )

    # When
    question_ids = kili.create_questions(
        project_id=project_id, text_array=questions, asset_id_array=asset_id_array
    )

    # Then
    assert len(question_ids) == 2
    mock_question_use_case_create_questions.assert_called_once_with(
        project_id=ProjectId("fake_project_id"),
        questions=[
            QuestionToCreateUseCaseInput(
                text="Where is the cat?",
                asset_id=AssetId("fake_asset_id_1"),
                asset_external_id=None,
            ),
            QuestionToCreateUseCaseInput(
                text="Where is the dog?",
                asset_id=AssetId("fake_asset_id_2"),
                asset_external_id=None,
            ),
        ],
    )
