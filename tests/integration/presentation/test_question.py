from kili.presentation.client.question import QuestionClientMethods


def test_create_questions():
    # Given
    questions = ["Where is the cat?", "Where is the dog?"]
    kili = QuestionClientMethods()
    project_id = "fake_project_id"
    asset_id_array = ["fake_asset_id_1", "fake_asset_id_2"]

    # When
    question_ids = kili.create_questions(
        project_id=project_id, text_array=questions, asset_id_array=asset_id_array
    )

    # Then
    assert len(question_ids) == 2
