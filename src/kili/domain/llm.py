"""API Key domain."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union


@dataclass
class OrganizationModelFilters:
    """Model filters for running a model search."""

    organization_id: str


class ModelType(str, Enum):
    AZURE_OPEN_AI = "AZURE_OPEN_AI"
    OPEN_AI_SDK = "OPEN_AI_SDK"


@dataclass
class AzureOpenAICredentials:
    api_key: str
    deployment_id: str
    endpoint: str


@dataclass
class OpenAISDKCredentials:
    api_key: str
    endpoint: str


@dataclass
class ModelToCreateInput:
    """Model to create use case input."""

    credentials: Union[AzureOpenAICredentials, OpenAISDKCredentials]
    name: str
    type: ModelType
    organization_id: str


@dataclass
class ModelToUpdateInput:
    """Model to update use case input."""

    credentials: Optional[Union[AzureOpenAICredentials, OpenAISDKCredentials]] = None
    name: Optional[str] = None


@dataclass
class ProjectModelToCreateInput:
    """Project model to create use case input."""

    project_id: str
    model_id: str
    configuration: dict


@dataclass
class ProjectModelFilters:
    """Project model filters for running a project model search."""

    project_id: Optional[str] = None
    model_id: Optional[str] = None
