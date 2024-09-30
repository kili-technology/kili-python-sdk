"""GraphQL payload data mappers for api keys operations."""

from typing import Dict

from kili.domain.llm import (
    AzureOpenAICredentials,
    ModelToCreateInput,
    ModelToUpdateInput,
    ModelType,
    OpenAISDKCredentials,
    OrganizationModelFilters,
    ProjectModelFilters,
    ProjectModelToCreateInput,
    ProjectModelToUpdateInput,
)


def model_where_wrapper(filter: OrganizationModelFilters) -> Dict:
    """Build the GraphQL ProjectMapperWhere variable to be sent in an operation."""
    return {
        "organizationId": filter.organization_id,
    }


def project_model_where_mapper(filter: ProjectModelFilters) -> Dict:
    """Build the GraphQL ProjectMapperWhere variable to be sent in an operation."""
    return {
        "projectId": filter.project_id,
        "modelId": filter.model_id,
    }


def map_create_model_input(data: ModelToCreateInput) -> Dict:
    """Build the GraphQL ModelInput variable to be sent in an operation."""
    if data.type == ModelType.AZURE_OPEN_AI and isinstance(
        data.credentials, AzureOpenAICredentials
    ):
        credentials = {
            "apiKey": data.credentials.api_key,
            "deploymentId": data.credentials.deployment_id,
            "endpoint": data.credentials.endpoint,
        }
    elif data.type == ModelType.OPEN_AI_SDK and isinstance(data.credentials, OpenAISDKCredentials):
        credentials = {"apiKey": data.credentials.api_key, "endpoint": data.credentials.endpoint}
    else:
        raise ValueError(
            f"Unsupported model type or credentials: {data.type}, {type(data.credentials)}"
        )

    return {
        "credentials": credentials,
        "name": data.name,
        "type": data.type.value,
        "organizationId": data.organization_id,
    }


def map_update_model_input(data: ModelToUpdateInput) -> Dict:
    """Build the GraphQL UpdateModelInput variable to be sent in an operation."""
    input_dict = {}
    if data.name is not None:
        input_dict["name"] = data.name

    if data.credentials is not None:
        if isinstance(data.credentials, AzureOpenAICredentials):
            credentials = {
                "apiKey": data.credentials.api_key,
                "deploymentId": data.credentials.deployment_id,
                "endpoint": data.credentials.endpoint,
            }
        elif isinstance(data.credentials, OpenAISDKCredentials):
            credentials = {
                "apiKey": data.credentials.api_key,
                "endpoint": data.credentials.endpoint,
            }
        else:
            raise ValueError(f"Unsupported credentials type: {type(data.credentials)}")
        input_dict["credentials"] = credentials

    return input_dict


def map_create_project_model_input(data: ProjectModelToCreateInput) -> Dict:
    """Build the GraphQL ModelInput variable to be sent in an operation."""
    return {
        "projectId": data.project_id,
        "modelId": data.model_id,
        "configuration": data.configuration,
    }


def map_update_project_model_input(data: ProjectModelToUpdateInput) -> Dict:
    """Build the GraphQL UpdateProjectModelInput variable to be sent in an operation."""
    input_dict = {}
    if data.configuration is not None:
        input_dict["configuration"] = data.configuration
    return input_dict


def map_delete_model_input(model_id: str) -> Dict:
    """Map the input for the GraphQL deleteModel mutation."""
    return {
        "deleteModelId": model_id,
    }


def map_delete_project_model_input(project_model_id: str) -> Dict:
    """Map the input for the GraphQL deleteProjectModel mutation."""
    return {
        "deleteProjectModelId": project_model_id,
    }


def map_create_llm_asset_input(data: Dict) -> Dict:
    """Map the input for the createLLMAsset mutation."""
    result = {
        "authorId": data["author_id"],
    }
    if "status" in data:
        result["status"] = data["status"]
    if "label_type" in data:
        result["labelType"] = data["label_type"]
    return result


def map_project_where(project_id: str) -> Dict:
    """Map the 'where' parameter for mutations that require a ProjectWhere."""
    return {"id": project_id}


def map_create_chat_item_input(label_id: str, prompt: str) -> Dict:
    """Map the input for the createChatItem mutation."""
    return {"content": prompt, "role": "USER", "labelId": label_id}


def map_asset_where(asset_id: str) -> Dict:
    """Map the 'where' parameter for the createChatItem mutation."""
    return {"id": asset_id}
