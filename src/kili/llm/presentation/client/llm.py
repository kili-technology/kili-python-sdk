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
from kili.domain.project import ProjectId
from kili.domain.project_model import (
    AzureOpenAICredentials,
    ModelToCreateInput,
    ModelType,
    OpenAISDKCredentials,
    OrganizationModelFilters,
    ProjectModelFilters,
)
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
    "name",
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

    def create_model(self, organization_id: str, model: dict):
        credentials_data = model.get("credentials")
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

    def delete_model(self, model_id: str):
        return self.kili_api_gateway.delete_model(model_id=model_id)

    def list_organization_models(
        self, organization_id: str, fields: Optional[List[str]] = None
    ) -> List[Dict]:
        """List models of given organization."""
        converted_filters = OrganizationModelFilters(
            organization_id=organization_id,
        )

        return list(
            self.kili_api_gateway.list_organization_models(
                filters=converted_filters,
                fields=fields if fields else DEFAULT_ORGANIZATION_MODEL_FIELDS,
            )
        )

    def list_project_models(
        self, project_id: str, filters: Optional[Dict] = None, fields: Optional[List[str]] = None
    ) -> List[Dict]:
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
