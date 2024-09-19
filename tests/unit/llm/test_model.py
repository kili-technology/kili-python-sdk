from kili.llm.presentation.client.llm import LlmClientMethods

mock_list_models = [
    {
        "id": "model_id_1",
        "credentials": {
            "apiKey": "***",
            "endpoint": "https://ai21-jamba-1-5-large-ykxca.eastus.models.ai.azure.com",
        },
        "name": "Jamba (created by SDK)",
        "type": "OPEN_AI_SDK",
    },
    {
        "id": "model_id_2",
        "credentials": {
            "apiKey": "***",
            "endpoint": "https://ai21-jamba-1-5-large-ykxca.eastus.models.ai.azure.com",
        },
        "name": "Jamba (created by SDK)",
        "type": "OPEN_AI_SDK",
    },
]
mock_get_model = {
    "id": "model_id",
    "credentials": {
        "apiKey": "***",
        "endpoint": "https://ai21-jamba-1-5-large-ykxca.eastus.models.ai.azure.com",
    },
    "name": "Jamba (created by SDK)",
    "type": "OPEN_AI_SDK",
}
mock_create_model = {"id": "new_model_id"}
mock_update_model = {
    "id": "model_id",
    "name": "Updated Model",
}
mock_delete_model = {"id": "model_id"}


def test_list_models(mocker):
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.list_models.return_value = mock_list_models

    kili_llm = LlmClientMethods(kili_api_gateway)
    result = kili_llm.list_models(organization_id="organization_id")

    assert result == mock_list_models


def test_get_model(mocker):
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.get_model.return_value = mock_get_model

    kili_llm = LlmClientMethods(kili_api_gateway)
    result = kili_llm.get_model(model_id="model_id")

    assert result == mock_get_model


def test_create_model(mocker):
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.create_model.return_value = mock_create_model

    kili_llm = LlmClientMethods(kili_api_gateway)
    result = kili_llm.create_model(
        organization_id="organization_id",
        model={
            "name": "New Model",
            "type": "OPEN_AI_SDK",
            "credentials": {
                "api_key": "***",
                "endpoint": "https://api.openai.com",
            },
        },
    )

    assert result == mock_create_model


def test_update_model(mocker):
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.get_model.return_value = mock_get_model
    kili_api_gateway.update_model.return_value = mock_update_model

    kili_llm = LlmClientMethods(kili_api_gateway)
    result = kili_llm.update_model(
        model_id="model_id",
        model={
            "name": "Updated Model",
            "credentials": {
                "api_key": "***",
                "endpoint": "https://api.openai.com",
            },
        },
    )

    assert result == mock_update_model


def test_delete_model(mocker):
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.delete_model.return_value = mock_delete_model

    kili_llm = LlmClientMethods(kili_api_gateway)
    result = kili_llm.delete_model(model_id="model_id")

    assert result == mock_delete_model
