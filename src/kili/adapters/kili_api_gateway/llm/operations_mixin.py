"""Mixin extending Kili API Gateway class with Api Keys related operations."""

from typing import Dict, List, Optional, cast

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.adapters.kili_api_gateway.llm.mappers import (
    map_asset_where,
    map_create_chat_item_input,
    map_create_llm_asset_input,
    map_create_model_input,
    map_create_project_model_input,
    map_delete_model_input,
    map_delete_project_model_input,
    map_project_where,
    map_update_model_input,
    map_update_project_model_input,
    model_where_wrapper,
    project_model_where_mapper,
)
from kili.adapters.kili_api_gateway.llm.operations import (
    get_create_chat_item_mutation,
    get_create_llm_asset_mutation,
    get_create_model_mutation,
    get_create_project_model_mutation,
    get_delete_model_mutation,
    get_delete_project_model_mutation,
    get_model_query,
    get_models_query,
    get_project_models_query,
    get_update_model_mutation,
    get_update_project_model_mutation,
)
from kili.domain.llm import (
    ChatItemDict,
    ModelDict,
    ModelToCreateInput,
    ModelToUpdateInput,
    OrganizationModelFilters,
    ProjectModelDict,
    ProjectModelFilters,
    ProjectModelToCreateInput,
    ProjectModelToUpdateInput,
)
from kili.domain.types import ListOrTuple

DEFAULT_PROJECT_FIELDS = ["id", "name", "credentials", "type"]
DEFAULT_PROJECT_MODEL_FIELDS = [
    "id",
    "configuration",
    "model.id",
    "model.credentials",
    "model.name",
    "model.type",
]


class ModelConfigurationOperationMixin(BaseOperationMixin):
    """Mixin extending Kili API Gateway class with model configuration related operations."""

    def list_models(
        self,
        filters: OrganizationModelFilters,
        fields: Optional[ListOrTuple[str]] = None,
        options: Optional[QueryOptions] = None,
    ) -> List[ModelDict]:
        """List models with given options."""
        fragment = fragment_builder(fields or DEFAULT_PROJECT_FIELDS)
        query = get_models_query(fragment)
        where = model_where_wrapper(filters)
        return [
            cast(ModelDict, item)
            for item in PaginatedGraphQLQuery(
                self.graphql_client
            ).execute_query_from_paginated_call(
                query,
                where,
                options if options else QueryOptions(disable_tqdm=False),
                "Retrieving organization models",
                None,
            )
        ]

    def get_model(self, model_id: str, fields: Optional[ListOrTuple[str]] = None) -> ModelDict:
        """Get a model by ID."""
        fragment = fragment_builder(fields or DEFAULT_PROJECT_FIELDS)
        query = get_model_query(fragment)
        variables = {"modelId": model_id}
        result = self.graphql_client.execute(query, variables)
        return result["model"]

    def create_model(self, model: ModelToCreateInput) -> ModelDict:
        """Send a GraphQL request calling createModel resolver."""
        payload = {"input": map_create_model_input(model)}
        fragment = fragment_builder(DEFAULT_PROJECT_FIELDS)
        mutation = get_create_model_mutation(fragment)
        result = self.graphql_client.execute(mutation, payload)
        return result["createModel"]

    def update_properties_in_model(self, model_id: str, model: ModelToUpdateInput) -> ModelDict:
        """Send a GraphQL request calling updateModel resolver."""
        payload = {"id": model_id, "input": map_update_model_input(model)}
        fragment = fragment_builder(DEFAULT_PROJECT_FIELDS)
        mutation = get_update_model_mutation(fragment)
        result = self.graphql_client.execute(mutation, payload)
        return result["updateModel"]

    def delete_model(self, model_id: str) -> bool:
        """Send a GraphQL request to delete an organization model."""
        payload = map_delete_model_input(model_id)
        mutation = get_delete_model_mutation()
        result = self.graphql_client.execute(mutation, payload)
        return result["deleteModel"]

    def create_project_model(self, project_model: ProjectModelToCreateInput) -> ProjectModelDict:
        """Send a GraphQL request calling createModel resolver."""
        payload = {"input": map_create_project_model_input(project_model)}
        fragment = fragment_builder(DEFAULT_PROJECT_MODEL_FIELDS)
        mutation = get_create_project_model_mutation(fragment)
        result = self.graphql_client.execute(mutation, payload)
        return result["createProjectModel"]

    def update_project_model(
        self, project_model_id: str, project_model: ProjectModelToUpdateInput
    ) -> ProjectModelDict:
        """Send a GraphQL request calling updateProjectModel resolver."""
        payload = {
            "updateProjectModelId": project_model_id,
            "input": map_update_project_model_input(project_model),
        }
        fragment = fragment_builder(DEFAULT_PROJECT_MODEL_FIELDS)
        mutation = get_update_project_model_mutation(fragment)
        result = self.graphql_client.execute(mutation, payload)
        return result["updateProjectModel"]

    def delete_project_model(self, project_model_id: str) -> bool:
        """Send a GraphQL request to delete a project model."""
        payload = map_delete_project_model_input(project_model_id)
        mutation = get_delete_project_model_mutation()
        result = self.graphql_client.execute(mutation, payload)
        return result["deleteProjectModel"]

    def list_project_models(
        self,
        filters: ProjectModelFilters,
        fields: Optional[ListOrTuple[str]] = None,
        options: Optional[QueryOptions] = None,
    ) -> List[ProjectModelDict]:
        """List project models with given options."""
        fragment = fragment_builder(fields or DEFAULT_PROJECT_MODEL_FIELDS)
        query = get_project_models_query(fragment)
        where = project_model_where_mapper(filters)
        return [
            cast(ProjectModelDict, item)
            for item in PaginatedGraphQLQuery(
                self.graphql_client
            ).execute_query_from_paginated_call(
                query,
                where,
                options if options else QueryOptions(disable_tqdm=False),
                "Retrieving project models",
                None,
            )
        ]

    def create_llm_asset(
        self,
        project_id: str,
        author_id: str,
        status: Optional[str] = None,
        label_type: Optional[str] = None,
    ) -> Dict:
        """Create an LLM asset in a project, with optional status and label_type."""
        where = map_project_where(project_id)
        data = {"author_id": author_id, "status": status, "label_type": label_type}
        data_mapped = map_create_llm_asset_input(data)
        variables = {"where": where, "data": data_mapped}
        fragment = fragment_builder(["id", "latestLabel.id"])
        mutation = get_create_llm_asset_mutation(fragment)
        result = self.graphql_client.execute(mutation, variables)
        return result["createLLMAsset"]

    def create_chat_item(self, asset_id: str, label_id: str, prompt: str) -> List[ChatItemDict]:
        """Create a chat item associated with an asset."""
        data = map_create_chat_item_input(label_id, prompt)
        where = map_asset_where(asset_id)
        variables = {"data": data, "where": where}
        fragment = fragment_builder(["content", "id", "labelId", "modelId", "parentId", "role"])
        mutation = get_create_chat_item_mutation(fragment)
        result = self.graphql_client.execute(mutation, variables)
        return [cast(ChatItemDict, item) for item in result["createChatItem"]]
