from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.domain.question import QuestionId
from kili.presentation.client.question import QuestionClientMethods


def test_create_one_question(kili_api_gateway: KiliAPIGateway):
    # given one issue to create
    kili = QuestionClientMethods()
    kili_api_gateway.create_questions.return_value = [{"id": QuestionId("created_question_id")}]

    kili.kili_api_gateway = kili_api_gateway

    # when creating one issue
    created_questions = kili.create_questions(
        project_id="project_id", text_array=["text"], asset_id_array=["asset_id"], disable_tqdm=True
    )

    # then
    assert created_questions[0]["id"] == "created_question_id"
