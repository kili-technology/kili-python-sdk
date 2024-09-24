from kili.llm.presentation.client.llm import LlmClientMethods

mock_list_project_models = [
    {
        "id": "project_model_id_1",
        "model": {
            "credentials": {
                "apiKey": "***",
                "endpoint": "https://ai21-jamba-1-5-large-ykxca.eastus.models.ai.azure.com",
            },
            "name": "Jamba (created by SDK)",
            "type": "OPEN_AI_SDK",
        },
        "configuration": {"model": "AI21-Jamba-1-5-Large-ykxca", "temperature": 0.5},
    },
    {
        "id": "project_model_id_2",
        "model": {
            "credentials": {
                "apiKey": "***",
                "endpoint": "https://ai21-jamba-1-5-large-ykxca.eastus.models.ai.azure.com",
            },
            "name": "Jamba (created by SDK)",
            "type": "OPEN_AI_SDK",
        },
        "configuration": {"model": "AI21-Jamba-1-5-Large-ykxca", "temperature": 0.7},
    },
]


def test_list_project_models(mocker):
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.list_project_models.return_value = mock_list_project_models

    kili_llm = LlmClientMethods(kili_api_gateway)
    result = kili_llm.project_models(project_id="project_id")

    assert result == mock_list_project_models


def test_create_project_model(mocker):
    mock_create_project_model = {"id": "new_project_model_id"}

    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.create_project_model.return_value = mock_create_project_model

    kili_llm = LlmClientMethods(kili_api_gateway)
    result = kili_llm.create_project_model(
        project_id="project_id",
        model_id="model_id",
        configuration={
            "model": "AI21-Jamba-1-5-Large-ykxca",
            "temperature": {"min": 0.2, "max": 0.8},
        },
    )

    assert result == mock_create_project_model


def test_update_project_model(mocker):
    mock_update_project_model = {
        "id": "project_model_id",
        "configuration": {"model": "AI21-Jamba-1-5-Large-ykxca", "temperature": 0.7},
    }

    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.update_project_model.return_value = mock_update_project_model

    kili_llm = LlmClientMethods(kili_api_gateway)
    result = kili_llm.update_project_model(
        project_model_id="project_model_id", configuration={"temperature": 0.7}
    )

    assert result == mock_update_project_model


def test_delete_project_model(mocker):
    mock_delete_project_model = {"id": "project_model_id"}

    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.delete_project_model.return_value = mock_delete_project_model

    kili_llm = LlmClientMethods(kili_api_gateway)
    result = kili_llm.delete_project_model(project_model_id="project_model_id")

    assert result == mock_delete_project_model
