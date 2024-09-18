"""GraphQL payload data mappers for api keys operations."""

from typing import Dict

from kili.domain.project_model import (
    ModelToCreateInput,
    ModelType,
    OrganizationModelFilters,
    ProjectModelFilters,
)


def organization_model_where_wrapper(filter: OrganizationModelFilters) -> Dict:
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
    if data.type == ModelType.AZURE_OPEN_AI:
        credentials = {
            "apiKey": data.credentials.api_key,
            "deploymentId": data.credentials.deployment_id,
            "endpoint": data.credentials.endpoint,
        }
    elif data.type == ModelType.OPEN_AI_SDK:
        credentials = {"apiKey": data.credentials.api_key, "endpoint": data.credentials.endpoint}
    else:
        raise ValueError(f"Unsupported model type: {data.type}")

    return {
        "credentials": credentials,
        "name": data.name,
        "type": data.type.value,
        "organizationId": data.organization_id,
    }


def map_delete_model_input(model_id: str) -> Dict:
    """Map the input for the GraphQL deleteModel mutation."""
    return {
        "deleteModelId": model_id,
    }
