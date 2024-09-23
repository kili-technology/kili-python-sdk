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

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.asset import AssetExternalId, AssetFilters, AssetId
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
from kili.domain.project import ProjectId
from kili.llm.services.export import export
from kili.services.export.exceptions import NoCompatibleJobError
from kili.use_cases.asset.utils import AssetUseCasesUtils
from kili.utils.logcontext import for_all_methods, log_call

DEFAULT_ORGANIZATION_MODEL_FIELDS = [
    "id",
    "credentials",
    "name",
    "type",
]

DEFAULT_PROJECT_MODEL_FIELDS = [
    "configuration",
    "id",
    "model.credentials",
    "model.name",
    "model.type",
]


@for_all_methods(log_call, exclude=["__init__"])
class LlmClientMethods:
    def __init__(self, kili_api_gateway: KiliAPIGateway):
        self.kili_api_gateway = kili_api_gateway

    def export(
        self,
        project_id: str,
        disable_tqdm: Optional[bool] = False,
        asset_ids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
    ) -> Optional[List[Dict[str, Union[List[str], str]]]]:
        # pylint: disable=line-too-long
        """Returns an export of llm assets with valid labels.

        Args:
            project_id: Identifier of the project.
            asset_ids: Optional list of the assets internal IDs from which to export the labels.
            disable_tqdm: Disable the progress bar if True.
            external_ids: Optional list of the assets external IDs from which to export the labels.

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

        asset_filter = AssetFilters(
            project_id=ProjectId(project_id), asset_id_in=resolved_asset_ids
        )

        try:
            return export(
                self.kili_api_gateway,
                project_id=ProjectId(project_id),
                asset_filter=asset_filter,
                disable_tqdm=disable_tqdm,
            )
        except NoCompatibleJobError as excp:
            warnings.warn(str(excp), stacklevel=2)
            return None

    def models(self, organization_id: str, fields: Optional[List[str]] = None):
        """List models of given organization."""
        converted_filters = OrganizationModelFilters(
            organization_id=organization_id,
        )

        return list(
            self.kili_api_gateway.list_models(
                filters=converted_filters,
                fields=fields if fields else DEFAULT_ORGANIZATION_MODEL_FIELDS,
            )
        )

    def model(self, model_id: str, fields: Optional[List[str]] = None):
        return self.kili_api_gateway.get_model(
            model_id=model_id,
            fields=fields if fields else DEFAULT_ORGANIZATION_MODEL_FIELDS,
        )

    def create_model(self, organization_id: str, model: dict):
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

    def update_properties_in_model(self, model_id: str, model: dict):
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

    def delete_model(self, model_id: str):
        return self.kili_api_gateway.delete_model(model_id=model_id)

    def project_models(
        self, project_id: str, filters: Optional[Dict] = None, fields: Optional[List[str]] = None
    ):
        """List project models of given project."""
        converted_filters = ProjectModelFilters(
            project_id=project_id,
            model_id=filters["model_id"] if filters and "model_id" in filters else None,
        )

        return list(
            self.kili_api_gateway.list_project_models(
                filters=converted_filters,
                fields=fields if fields else DEFAULT_PROJECT_MODEL_FIELDS,
            )
        )

    def create_project_model(self, project_id: str, model_id: str, configuration: dict):
        project_model_input = ProjectModelToCreateInput(
            project_id=project_id, model_id=model_id, configuration=configuration
        )
        return self.kili_api_gateway.create_project_model(project_model=project_model_input)

    def update_project_model(self, project_model_id: str, configuration: dict):
        project_model_input = ProjectModelToUpdateInput(configuration=configuration)
        return self.kili_api_gateway.update_project_model(
            project_model_id=project_model_id, project_model=project_model_input
        )

    def delete_project_model(self, project_model_id: str):
        return self.kili_api_gateway.delete_project_model(project_model_id)

    def create_conversation(self, project_id: str, prompt: str):
        user_id = self.kili_api_gateway.get_current_user(["id"])["id"]
        llm_asset = self.kili_api_gateway.create_llm_asset(
            project_id=project_id,
            author_id=user_id,
            status="TODO",
            label_type="PREDICTION",
        )
        asset_id = llm_asset["id"]
        label_id = llm_asset["latestLabel"]["id"]
        return self.kili_api_gateway.create_chat_item(
            asset_id=asset_id, label_id=label_id, prompt=prompt
        )
