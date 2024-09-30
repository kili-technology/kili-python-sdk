"""LLM domain."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Union

from typing_extensions import TypedDict


@dataclass
class OrganizationModelFilters:
    """Model filters for running a model search."""

    organization_id: str


class ModelType(str, Enum):
    """Enumeration of the supported model types.

    - `AZURE_OPEN_AI`: Models hosted on Microsoft Azure's OpenAI service.
    - `OPEN_AI_SDK`: Models provided via OpenAI's SDK.
    """

    AZURE_OPEN_AI = "AZURE_OPEN_AI"
    OPEN_AI_SDK = "OPEN_AI_SDK"


@dataclass
class AzureOpenAICredentials:
    """Credentials for accessing Azure OpenAI models.

    Attributes:
    - `api_key`: The API key required for authentication to Azure OpenAI.
    - `deployment_id`: The specific deployment of the model within Azure.
    - `endpoint`: The endpoint URL where the Azure OpenAI service is hosted.
    """

    api_key: str
    deployment_id: str
    endpoint: str


@dataclass
class OpenAISDKCredentials:
    """Credentials for accessing OpenAI SDK models.

    Attributes:
    - `api_key`: The API key required for authentication to OpenAI's SDK.
    - `endpoint`: The endpoint URL where the OpenAI SDK service is hosted.
    """

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
class ProjectModelToUpdateInput:
    """Project model to update use case input."""

    configuration: Optional[dict] = None


@dataclass
class ProjectModelFilters:
    """Project model filters for running a project model search."""

    project_id: Optional[str] = None
    model_id: Optional[str] = None


class ChatItemRole(str, Enum):
    """Enumeration of the supported chat item role."""

    ASSISTANT = "ASSISTANT"
    USER = "USER"


class OpenAISDKCredentialsDict(TypedDict):
    """Dict that represents model.Credentials for OpenAI SDK."""

    api_key: str
    endpoint: str


class AzureOpenAICredentialsDict(TypedDict):
    """Dict that represents model.Credentials for Azure OpenAI."""

    api_key: str
    endpoint: str
    deployment_id: str


class ModelDict(TypedDict):
    """Dict that represents a Model."""

    id: str
    credentials: Union[AzureOpenAICredentialsDict, OpenAISDKCredentialsDict]
    name: str
    type: str


class ProjectModelDict(TypedDict):
    """Dict that represents a ProjectModel."""

    id: str
    configuration: Dict[str, Any]
    model: ModelDict


class ChatItemDict(TypedDict):
    """Dict that represents a ChatItem."""

    content: str
    id: str
    role: ChatItemRole
