import pytest

from kili.adapters.kili_api_gateway.llm.mappers import (
    map_create_model_input,
    map_update_model_input,
)
from kili.domain.llm import (
    AzureOpenAICredentials,
    ModelToCreateInput,
    ModelToUpdateInput,
    ModelType,
    OpenAISDKCredentials,
)
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
mock_get_model_open_ai_sdk = {
    "id": "model_id",
    "credentials": {
        "apiKey": "***",
        "endpoint": "https://ai21-jamba-1-5-large-ykxca.eastus.models.ai.azure.com",
    },
    "name": "Jamba (created by SDK)",
    "type": "OPEN_AI_SDK",
}
mock_get_model_azure_open_ai = {
    "id": "model_id",
    "credentials": {
        "apiKey": "***",
        "endpoint": "https://ai21-jamba-1-5-large-ykxca.eastus.models.ai.azure.com",
        "deploymentId": "deployment_id",
    },
    "name": "Jamba (created by SDK)",
    "type": "AZURE_OPEN_AI",
}
mock_create_model = {"id": "new_model_id"}
mock_update_model = {
    "id": "model_id",
    "name": "Updated Model",
}
mock_delete_model = {"id": "model_id"}


def test_map_create_model_input_with_openai_sdk_credentials():
    credentials = OpenAISDKCredentials(api_key="api_key", endpoint="https://api.openai.com/v1/")
    input_data = ModelToCreateInput(
        name="Test Model",
        type=ModelType.OPEN_AI_SDK,
        organization_id="org_id",
        credentials=credentials,
    )
    expected_output = {
        "credentials": {
            "apiKey": "api_key",
            "endpoint": "https://api.openai.com/v1/",
        },
        "name": "Test Model",
        "type": ModelType.OPEN_AI_SDK.value,
        "organizationId": "org_id",
    }

    result = map_create_model_input(input_data)
    assert result == expected_output


def test_map_create_model_input_with_azure_openai_credentials():
    credentials = AzureOpenAICredentials(
        api_key="api_key",
        deployment_id="deployment_id",
        endpoint="https://azure-openai-endpoint.com",
    )
    input_data = ModelToCreateInput(
        name="Test Azure Model",
        type=ModelType.AZURE_OPEN_AI,
        organization_id="org_id",
        credentials=credentials,
    )
    expected_output = {
        "credentials": {
            "apiKey": "api_key",
            "deploymentId": "deployment_id",
            "endpoint": "https://azure-openai-endpoint.com",
        },
        "name": "Test Azure Model",
        "type": ModelType.AZURE_OPEN_AI.value,
        "organizationId": "org_id",
    }

    result = map_create_model_input(input_data)
    assert result == expected_output


def test_map_update_model_input_update_name_only():
    input_data = ModelToUpdateInput(name="Updated Model Name")
    expected_output = {"name": "Updated Model Name"}

    result = map_update_model_input(input_data)
    assert result == expected_output


def test_map_update_model_input_update_openai_sdk_credentials():
    credentials = OpenAISDKCredentials(
        api_key="new_api_key", endpoint="https://new-openai-endpoint.com"
    )
    input_data = ModelToUpdateInput(credentials=credentials)
    expected_output = {
        "credentials": {
            "apiKey": "new_api_key",
            "endpoint": "https://new-openai-endpoint.com",
        }
    }

    result = map_update_model_input(input_data)
    assert result == expected_output


def test_map_update_model_input_update_azure_openai_credentials():
    credentials = AzureOpenAICredentials(
        api_key="new_api_key",
        deployment_id="new_deployment_id",
        endpoint="https://new-azure-openai-endpoint.com",
    )
    input_data = ModelToUpdateInput(credentials=credentials)
    expected_output = {
        "credentials": {
            "apiKey": "new_api_key",
            "deploymentId": "new_deployment_id",
            "endpoint": "https://new-azure-openai-endpoint.com",
        }
    }

    result = map_update_model_input(input_data)
    assert result == expected_output


def test_map_update_model_input_update_name_and_openai_sdk_credentials():
    credentials = OpenAISDKCredentials(
        api_key="new_api_key", endpoint="https://new-openai-endpoint.com"
    )
    input_data = ModelToUpdateInput(name="Updated Model Name", credentials=credentials)
    expected_output = {
        "name": "Updated Model Name",
        "credentials": {
            "apiKey": "new_api_key",
            "endpoint": "https://new-openai-endpoint.com",
        },
    }

    result = map_update_model_input(input_data)
    assert result == expected_output


def test_map_update_model_input_update_name_and_azure_openai_credentials():
    credentials = AzureOpenAICredentials(
        api_key="new_api_key",
        deployment_id="new_deployment_id",
        endpoint="https://new-azure-openai-endpoint.com",
    )
    input_data = ModelToUpdateInput(name="Updated Model Name", credentials=credentials)
    expected_output = {
        "name": "Updated Model Name",
        "credentials": {
            "apiKey": "new_api_key",
            "deploymentId": "new_deployment_id",
            "endpoint": "https://new-azure-openai-endpoint.com",
        },
    }

    result = map_update_model_input(input_data)
    assert result == expected_output


def test_map_update_model_input_no_updates():
    input_data = ModelToUpdateInput()
    expected_output = {}

    result = map_update_model_input(input_data)
    assert result == expected_output


def test_list_models(mocker):
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.list_models.return_value = mock_list_models

    kili_llm = LlmClientMethods(kili_api_gateway)
    result = kili_llm.models(organization_id="organization_id")

    assert result == mock_list_models


def test_get_model(mocker):
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.get_model.return_value = mock_get_model_open_ai_sdk

    kili_llm = LlmClientMethods(kili_api_gateway)
    result = kili_llm.model(model_id="model_id")

    assert result == mock_get_model_open_ai_sdk


def test_create_model_open_ai_sdk(mocker):
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


def test_create_model_azure_openai(mocker):
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.create_model.return_value = mock_create_model

    kili_llm = LlmClientMethods(kili_api_gateway)
    result = kili_llm.create_model(
        organization_id="organization_id",
        model={
            "name": "New Model",
            "type": "AZURE_OPEN_AI",
            "credentials": {
                "api_key": "***",
                "endpoint": "https://api.openai.com",
                "deployment_id": "deployment_id",
            },
        },
    )

    assert result == mock_create_model


def test_create_invalid_model(mocker):
    kili_api_gateway = mocker.MagicMock()
    kili_llm = LlmClientMethods(kili_api_gateway)

    with pytest.raises(ValueError):
        kili_llm.create_model(
            organization_id="organization_id",
            model={
                "name": "New Model",
                "type": "Wrong type",
                "credentials": {"api_key": "***", "endpoint": "https://api.openai.com"},
            },
        )


def test_update_model_open_ai_sdk(mocker):
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.get_model.return_value = mock_get_model_open_ai_sdk
    kili_api_gateway.update_properties_in_model.return_value = mock_update_model

    kili_llm = LlmClientMethods(kili_api_gateway)
    result = kili_llm.update_properties_in_model(
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


def test_update_model_azure_open_ai(mocker):
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.get_model.return_value = mock_get_model_azure_open_ai
    kili_api_gateway.update_properties_in_model.return_value = mock_update_model

    kili_llm = LlmClientMethods(kili_api_gateway)
    result = kili_llm.update_properties_in_model(
        model_id="model_id",
        model={
            "name": "Updated Model",
            "credentials": {
                "api_key": "***",
                "endpoint": "https://api.openai.com",
                "deployment_id": "deployment_id",
            },
        },
    )

    assert result == mock_update_model


def test_update_invalid_model(mocker):
    kili_api_gateway = mocker.MagicMock()
    kili_llm = LlmClientMethods(kili_api_gateway)

    with pytest.raises(ValueError):
        kili_llm.update_properties_in_model(
            model_id="model_id",
            model={
                "name": "New Model",
                "type": "Wrong type",
                "credentials": {"api_key": "***", "endpoint": "https://api.openai.com"},
            },
        )


def test_update_non_existing_model(mocker):
    kili_api_gateway = mocker.MagicMock()
    kili_llm = LlmClientMethods(kili_api_gateway)
    kili_api_gateway.get_model.return_value = None

    with pytest.raises(ValueError):
        kili_llm.update_properties_in_model(
            model_id="model_id",
            model={
                "name": "New Model",
                "type": "Wrong type",
                "credentials": {"api_key": "***", "endpoint": "https://api.openai.com"},
            },
        )


def test_delete_model(mocker):
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.delete_model.return_value = mock_delete_model

    kili_llm = LlmClientMethods(kili_api_gateway)
    result = kili_llm.delete_model(model_id="model_id")

    assert result == mock_delete_model
