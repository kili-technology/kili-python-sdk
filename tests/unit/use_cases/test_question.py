from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.question.types import QuestionsToCreateGatewayInput
from kili.domain.project import ProjectId
from kili.domain.question import QuestionId
from kili.use_cases.question import QuestionUseCases


def test_create_one_question(kili_api_gateway: KiliAPIGateway):
    # given one issue to create
    kili_api_gateway.create_questions.return_value = (
        q for q in [{"id": QuestionId("created_question_id")}]
    )
    question = QuestionsToCreateGatewayInput(text="text", asset_id="asset_id")

    # when creating one issue
    created_questions = QuestionUseCases(kili_api_gateway).create_questions(
        project_id=ProjectId("project_id"), questions=[question], disable_tqdm=True
    )

    # then
    assert "created_question_id" == next(created_questions)["id"]
