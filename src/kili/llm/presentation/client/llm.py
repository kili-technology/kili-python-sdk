"""Client presentation methods for labels."""

# pylint: disable=too-many-lines
import warnings
from typing import (
    Dict,
    List,
    Optional,
    Union,
    cast,
)

from kili_formats.types import ChatItem, ChatItemRole, Conversation

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.asset import AssetExternalId, AssetFilters, AssetId, AssetStatus
from kili.domain.asset.asset import StatusInStep
from kili.domain.label import LabelType
from kili.domain.llm import (
    AzureOpenAICredentials,
    ModelDict,
    ModelToCreateInput,
    ModelToUpdateInput,
    ModelType,
    OpenAISDKCredentials,
    OrganizationModelFilters,
    ProjectModelDict,
    ProjectModelFilters,
    ProjectModelToCreateInput,
    ProjectModelToUpdateInput,
)
from kili.domain.project import ProjectId
from kili.llm.services.export import export
from kili.presentation.client.helpers.filter_conversion import convert_step_in_to_step_id_in_filter
from kili.services.export.exceptions import NoCompatibleJobError
from kili.use_cases.asset.utils import AssetUseCasesUtils
from kili.use_cases.project.project import ProjectUseCases
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class LlmClientMethods:
    def __init__(self, kili_api_gateway: KiliAPIGateway):
        self.kili_api_gateway = kili_api_gateway

    def import_conversations(
        self,
        project_id: str,
        conversations: List[Conversation],
    ):
        """Import conversations into a LLM Static project.

        Args:
            project_id: Identifier of the project.
            conversations: List of conversations to import. Each conversation should be a dictionary with the following keys
                - `chatItems`: List of chat items in the conversation. Each chat item should be a dictionary with the following keys
                    - `content`: (required) Content of the chat item.
                    - `externalId`: (required) Identifier of the chat item (must be unique).
                    - `modelName`: Name of the model that generated the chat item. Required only for ASSISTANT chat items.
                    - `role`: (required) Role of the chat item, one of `SYSTEM`, `USER` or `ASSISTANT`.
                - `externalId`: (required) Identifier of the conversation (must be unique).
                - `label`: (optional) Label associated with the conversation. Should be a dictionary with the following keys
                    - `conversation`
                    - `completion`
                    - `round`
                - `labeler`: (optional) Email of the labeler associated with the conversation.
                - `metadata`: (optional) Additional metadata associated with the conversation.

        Returns:
            A dict containing following keys
            - `numberOfUploadedAssets`: Number of assets uploaded.
            - `warnings`: List of detailed warnings generated during the import process, for each conversation.
        """
        return self.kili_api_gateway.import_conversations(
            project_id=project_id, conversations=conversations
        )

    def export(
        self,
        project_id: str,
        disable_tqdm: Optional[bool] = False,
        asset_ids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
        include_sent_back_labels: Optional[bool] = False,
        label_type_in: Optional[List[LabelType]] = None,
        status_in: Optional[List[AssetStatus]] = None,
        step_name_in: Optional[List[str]] = None,
        step_status_in: Optional[List[StatusInStep]] = None,
    ) -> Optional[Union[List[Conversation], List[Dict[str, Union[List[str], str]]]]]:
        """Returns an export of llm conversations with valid labels.

        Args:
            project_id: Identifier of the project.
            asset_ids: Optional list of the assets internal IDs from which to export the labels.
            disable_tqdm: Disable the progress bar if True.
            external_ids: Optional list of the assets external IDs from which to export the labels.
            include_sent_back_labels: Include sent back labels if True.
            label_type_in: Optional types of label to fetch, by default ["DEFAULT", "REVIEW"].
            status_in: Returned assets should have a status that belongs to that list, if given.
                Possible choices: `TODO`, `ONGOING`, `LABELED`, `TO_REVIEW` or `REVIEWED`.
            step_name_in: Returned assets are in a step whose name belong to that list, if given.
                Only applicable if the project is in WorkflowV2.
            step_status_in: Returned assets have the status of their step that belongs to that list, if given.
                Possible choices: `TO_DO`, `DOING`, `PARTIALLY_DONE`, `REDO`, `DONE`, `SKIPPED`.
                Only applicable if the project is in WorkflowV2.
        !!! Example
            ```python
            kili.llm.export("your_project_id")
            ```
        """
        if asset_ids and external_ids:
            raise ValueError("You cannot provide both asset_ids and external_ids")

        if external_ids is not None and asset_ids is None:
            id_map = AssetUseCasesUtils(self.kili_api_gateway).infer_ids_from_external_ids(
                asset_external_ids=cast(List[AssetExternalId], external_ids),
                project_id=ProjectId(project_id),
            )
            resolved_asset_ids = [id_map[AssetExternalId(i)] for i in external_ids]
        else:
            resolved_asset_ids = (
                list(AssetId(asset_id) for asset_id in asset_ids) if asset_ids else None
            )

        label_type_in = label_type_in or ["DEFAULT", "REVIEW"]

        step_id_in = None

        if status_in is not None or step_name_in is not None or step_status_in is not None:
            project_use_cases = ProjectUseCases(self.kili_api_gateway)
            step_id_in = convert_step_in_to_step_id_in_filter(
                project_steps=project_use_cases.get_project_steps(project_id),
                asset_filter_kwargs={
                    "step_name_in": step_name_in,
                    "step_status_in": step_status_in,
                    "status_in": status_in,
                },
            )

        asset_filter = AssetFilters(
            project_id=ProjectId(project_id),
            asset_id_in=resolved_asset_ids,
            label_type_in=label_type_in,
            status_in=status_in,
            step_id_in=step_id_in,
            step_status_in=step_status_in,
        )

        try:
            return export(
                self.kili_api_gateway,
                project_id=ProjectId(project_id),
                asset_filter=asset_filter,
                disable_tqdm=disable_tqdm,
                include_sent_back_labels=include_sent_back_labels,
                label_type_in=label_type_in,
            )
        except NoCompatibleJobError as excp:
            warnings.warn(str(excp), stacklevel=2)
            return None

    def create_model(self, organization_id: str, model: dict) -> ModelDict:
        """Create a new model in an organization.

        Args:
            organization_id: Identifier of the organization.
            model: A dictionary representing the model to create, containing:
                - `name`: Name of the model.
                - `type`: Type of the model, one of:
                    - `"AZURE_OPEN_AI"`
                    - `"OPEN_AI_SDK"`
                - `credentials`: Credentials required for the model, depending on the type:
                    - For `"AZURE_OPEN_AI"` type:
                        - `api_key`: The API key for Azure OpenAI.
                        - `deployment_id`: The deployment ID within Azure.
                        - `endpoint`: The endpoint URL of the Azure OpenAI service.
                    - For `"OPEN_AI_SDK"` type:
                        - `api_key`: The API key for OpenAI SDK.
                        - `endpoint`: The endpoint URL of the OpenAI SDK service.

        Returns:
            A dictionary containing the created model's details.

        Examples:
            >>> # Example of creating an OpenAI SDK model
            >>> model_data = {
            ...     "name": "My OpenAI SDK Model",
            ...     "type": "OPEN_AI_SDK",
            ...     "credentials": {
            ...         "api_key": "your_open_ai_api_key",
            ...         "endpoint": "your_open_ai_endpoint"
            ...     }
            ... }
            >>> kili.llm.create_model(organization_id="your_organization_id", model=model_data)
        """
        credentials_data = model["credentials"]
        model_type = ModelType(model["type"])

        if model_type == ModelType.AZURE_OPEN_AI:
            credentials = AzureOpenAICredentials(**credentials_data)
        elif model_type == ModelType.OPEN_AI_SDK:
            credentials = OpenAISDKCredentials(**credentials_data)
        else:
            raise ValueError(f"Unsupported model type: {model['type']}")

        model_input = ModelToCreateInput(
            credentials=credentials,
            name=model["name"],
            type=model_type,
            organization_id=organization_id,
        )
        return self.kili_api_gateway.create_model(model=model_input)

    def models(self, organization_id: str, fields: Optional[List[str]] = None) -> List[ModelDict]:
        """List models in an organization.

        Args:
            organization_id: Identifier of the organization.
            fields: All the fields to request among the possible fields for the models.
                Defaults to ["id", "credentials", "name", "type"].

        Returns:
            A list of models.

        Examples:
            >>> kili.llm.models(organization_id="your_organization_id")
        """
        converted_filters = OrganizationModelFilters(
            organization_id=organization_id,
        )

        return list(self.kili_api_gateway.list_models(filters=converted_filters, fields=fields))

    def model(self, model_id: str, fields: Optional[List[str]] = None) -> ModelDict:
        """Retrieve a specific model.

        Args:
            model_id: Identifier of the model.
            fields: All the fields to request among the possible fields for the models.
                Defaults to ["id", "credentials", "name", "type"].

        Returns:
            A dictionary representing the model.

        Examples:
            >>> kili.llm.model(model_id="your_model_id")
        """
        return self.kili_api_gateway.get_model(
            model_id=model_id,
            fields=fields,
        )

    def update_properties_in_model(self, model_id: str, model: dict) -> ModelDict:
        """Update properties of an existing model.

        Args:
            model_id: Identifier of the model to update.
            model: A dictionary containing the properties to update, which may include:
                - `name`: New name of the model.
                - `credentials`: Updated credentials for the model, depending on the type:
                    - For `"AZURE_OPEN_AI"` type:
                        - `api_key`: The API key for Azure OpenAI.
                        - `deployment_id`: The deployment ID within Azure.
                        - `endpoint`: The endpoint URL of the Azure OpenAI service.
                    - For `"OPEN_AI_SDK"` type:
                        - `api_key`: The API key for OpenAI SDK.
                        - `endpoint`: The endpoint URL of the OpenAI SDK service.

        Returns:
            A dictionary containing the updated model's details.

        Examples:
            >>> # Update the name of a model
            >>> kili.llm.update_properties_in_model(
            ...     model_id="your_model_id",
            ...     model={"name": "Updated Model Name"}
            ... )
        """
        credentials_data = model.get("credentials")
        credentials = None

        if credentials_data:
            existing_model = self.kili_api_gateway.get_model(
                model_id=model_id, fields=["id", "type"]
            )
            if not existing_model:
                raise ValueError(f"Model with id {model_id} not found")
            model_type = ModelType(existing_model["type"])

            if model_type == ModelType.AZURE_OPEN_AI:
                credentials = AzureOpenAICredentials(**credentials_data)
            elif model_type == ModelType.OPEN_AI_SDK:
                credentials = OpenAISDKCredentials(**credentials_data)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")

        model_input = ModelToUpdateInput(
            credentials=credentials,
            name=model.get("name"),
        )
        return self.kili_api_gateway.update_properties_in_model(
            model_id=model_id, model=model_input
        )

    def delete_model(self, model_id: str) -> bool:
        """Delete a model from an organization.

        Args:
            model_id: Identifier of the model to delete.

        Returns:
            A dictionary indicating the result of the deletion.

        Examples:
            >>> kili.llm.delete_model(model_id="your_model_id")
        """
        return self.kili_api_gateway.delete_model(model_id=model_id)

    def create_project_model(
        self, project_id: str, model_id: str, configuration: dict
    ) -> ProjectModelDict:
        """Associate a model with a project.

        Args:
            project_id: Identifier of the project.
            model_id: Identifier of the model to associate.
            configuration: Configuration parameters for the project model.

        Returns:
            A dictionary containing the created project model's details.

        Examples:
            >>> configuration = {
            ...     # Configuration details specific to your use case
            ... }
            >>> kili.llm.create_project_model(
            ...     project_id="your_project_id",
            ...     model_id="your_model_id",
            ...     configuration={"temperature": 0.7}
            ... )
        """
        project_model_input = ProjectModelToCreateInput(
            project_id=project_id, model_id=model_id, configuration=configuration
        )
        return self.kili_api_gateway.create_project_model(project_model=project_model_input)

    def project_models(
        self, project_id: str, filters: Optional[Dict] = None, fields: Optional[List[str]] = None
    ) -> List[ProjectModelDict]:
        """List models associated with a project.

        Args:
            project_id: Identifier of the project.
            filters: Optional filters to apply. Possible keys:
                - `model_id`: Identifier of a specific model to filter by.
            fields: All the fields to request among the possible fields for the project models.
                Defaults to ["configuration", "id", "model.credentials", "model.name", "model.type"].

        Returns:
            A list of project models.

        Examples:
            >>> kili.llm.project_models(project_id="your_project_id")
        """
        converted_filters = ProjectModelFilters(
            project_id=project_id,
            model_id=filters["model_id"] if filters and "model_id" in filters else None,
        )

        return list(
            self.kili_api_gateway.list_project_models(
                filters=converted_filters,
                fields=fields,
            )
        )

    def update_project_model(self, project_model_id: str, configuration: dict) -> ProjectModelDict:
        """Update the configuration of a project model.

        Args:
            project_model_id: Identifier of the project model to update.
            configuration: New configuration parameters.

        Returns:
            A dictionary containing the updated project model's details.

        Examples:
            >>> configuration = {
            ...     # Updated configuration details
            ... }
            >>> kili.llm.update_project_model(
            ...     project_model_id="your_project_model_id",
            ...     configuration=configuration
            ... )
        """
        project_model_input = ProjectModelToUpdateInput(configuration=configuration)
        return self.kili_api_gateway.update_project_model(
            project_model_id=project_model_id, project_model=project_model_input
        )

    def delete_project_model(self, project_model_id: str) -> bool:
        """Delete a project model.

        Args:
            project_model_id: Identifier of the project model to delete.

        Returns:
            A dictionary indicating the result of the deletion.

        Examples:
            >>> kili.llm.delete_project_model(project_model_id="your_project_model_id")
        """
        return self.kili_api_gateway.delete_project_model(project_model_id)

    def list_chat_items(self, asset_id: str) -> List[ChatItem]:
        """List chat items associated with an asset.

        Args:
            asset_id: Identifier of the asset.

        Returns:
            A list of chat items associated with the asset.

        Examples:
            >>> kili.llm.list_chat_items(asset_id="your_asset_id")
        """
        return self.kili_api_gateway.list_chat_items(asset_id=asset_id)

    def create_conversation(
        self, project_id: str, initial_prompt: str, system_prompt: Optional[str] = None
    ) -> List[ChatItem]:
        """Create a new conversation in an LLM project starting with a user's prompt.

        This method initiates a new conversation in the specified project by:
        - Creating an LLM asset and label associated with the current user.
        - Adding the user's prompt as the first chat item.
        - Automatically generating assistant responses using the project's models.

        Args:
            project_id: The identifier of the project where the conversation will be created.
            initial_prompt: The initial prompt or message from the user to start the conversation.
            system_prompt: Optional system prompt to guide the assistant's responses.

        Returns:
            A list of chat items in the conversation, including the user's prompts and the assistant's responses.

        Examples:
            >>> PROMPT = "Hello, how can I improve my coding skills?"
            >>> chat_items = kili.llm.create_conversation(project_id="your_project_id", prompt=PROMPT)

        Notes:
            - The first chat item corresponds to the user's prompt.
            - The subsequent chat items are assistant responses generated by the project's models.
            - An LLM asset and a label are created in the project with labelType "PREDICTION".
        """
        user_id = self.kili_api_gateway.get_current_user(["id"])["id"]
        llm_asset = self.kili_api_gateway.create_llm_asset(
            project_id=project_id,
            author_id=user_id,
            label_type="PREDICTION",
        )
        asset_id = llm_asset["id"]
        label_id = llm_asset["latestLabel"]["id"]

        system_chat_item = []
        if system_prompt:
            system_chat_item = self.kili_api_gateway.create_chat_item(
                asset_id=asset_id, label_id=label_id, prompt=system_prompt, role=ChatItemRole.SYSTEM
            )

        parent_id = system_chat_item[0]["id"] if system_chat_item else None
        prompt_chat_item = self.kili_api_gateway.create_chat_item(
            asset_id=asset_id,
            label_id=label_id,
            prompt=initial_prompt,
            role=ChatItemRole.USER,
            parent_id=parent_id,
        )

        return system_chat_item + prompt_chat_item
