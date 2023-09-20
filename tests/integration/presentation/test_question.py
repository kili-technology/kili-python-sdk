from typing import List, Optional, cast

from kili.domain.question import QuestionId
from kili.presentation.client.question import QuestionClientMethods


def test_create_questions(mocker, kili_api_gateway):
    # Given
    questions = cast(List[Optional[str]], ["Where is the cat?", "Where is the dog?"])
    kili = QuestionClientMethods()
    kili.kili_api_gateway = kili_api_gateway
    kili.kili_api_gateway.create_issues = mocker.MagicMock(
        return_value=[QuestionId("1"), QuestionId("2")]
    )
    project_id = "fake_project_id"
    asset_id_array = ["fake_asset_id_1", "fake_asset_id_2"]

    # When
    question_ids = kili.create_questions(
        project_id=project_id, text_array=questions, asset_id_array=asset_id_array
    )

    # Then
    assert len(question_ids) == 2
    kili.kili_api_gateway.create_issues.assert_called_once()
