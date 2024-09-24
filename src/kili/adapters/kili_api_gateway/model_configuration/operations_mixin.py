"""Mixin extending Kili API Gateway class with Api Keys related operations."""

from typing import Dict, Generator, Optional

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.adapters.kili_api_gateway.model_configuration.mappers import (
    map_create_model_input,
    map_create_project_model_input,
    map_delete_model_input,
    map_delete_project_model_input,
    map_update_model_input,
    map_update_project_model_input,
    model_where_wrapper,
    project_model_where_mapper,
)
from kili.adapters.kili_api_gateway.model_configuration.operations import (
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
    ModelToCreateInput,
    ModelToUpdateInput,
    OrganizationModelFilters,
    ProjectModelFilters,
    ProjectModelToCreateInput,
    ProjectModelToUpdateInput,
)
from kili.domain.types import ListOrTuple


class ModelConfigurationOperationMixin(BaseOperationMixin):
    """Mixin extending Kili API Gateway class with model configuration related operations."""

    def list_models(
        self,
        filters: OrganizationModelFilters,
        fields: ListOrTuple[str],
        options: Optional[QueryOptions] = None,
    ) -> Generator[Dict, None, None]:
        """List models with given options."""
        fragment = fragment_builder(fields)
        query = get_models_query(fragment)
        where = model_where_wrapper(filters)
        return PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query,
            where,
            options if options else QueryOptions(disable_tqdm=False),
            "Retrieving organization models",
            None,
        )

    def get_model(self, model_id: str, fields: ListOrTuple[str]) -> Dict:
        """Get a model by ID."""
        fragment = fragment_builder(fields)
        query = get_model_query(fragment)
        variables = {"modelId": model_id}
        result = self.graphql_client.execute(query, variables)
        return result["model"]

    def create_model(self, model: ModelToCreateInput) -> Dict:
        """Send a GraphQL request calling createModel resolver."""
        payload = {"input": map_create_model_input(model)}
        fragment = fragment_builder(["id"])
        mutation = get_create_model_mutation(fragment)
        result = self.graphql_client.execute(mutation, payload)
        return result["createModel"]

    def update_properties_in_model(self, model_id: str, model: ModelToUpdateInput) -> Dict:
        """Send a GraphQL request calling updateModel resolver."""
        payload = {"id": model_id, "input": map_update_model_input(model)}
        fragment = fragment_builder(["id"])
        mutation = get_update_model_mutation(fragment)
        result = self.graphql_client.execute(mutation, payload)
        return result["updateModel"]

    def delete_model(self, model_id: str) -> Dict:
        """Send a GraphQL request to delete an organization model."""
        payload = map_delete_model_input(model_id)
        mutation = get_delete_model_mutation()
        result = self.graphql_client.execute(mutation, payload)
        return result["deleteModel"]

    def create_project_model(self, project_model: ProjectModelToCreateInput) -> Dict:
        """Send a GraphQL request calling createModel resolver."""
        payload = {"input": map_create_project_model_input(project_model)}
        fragment = fragment_builder(["id"])
        mutation = get_create_project_model_mutation(fragment)
        result = self.graphql_client.execute(mutation, payload)
        return result["createProjectModel"]

    def update_project_model(
        self, project_model_id: str, project_model: ProjectModelToUpdateInput
    ) -> Dict:
        """Send a GraphQL request calling updateProjectModel resolver."""
        payload = {
            "updateProjectModelId": project_model_id,
            "input": map_update_project_model_input(project_model),
        }
        fragment = fragment_builder(["id", "configuration"])
        mutation = get_update_project_model_mutation(fragment)
        result = self.graphql_client.execute(mutation, payload)
        return result["updateProjectModel"]

    def delete_project_model(self, project_model_id: str) -> Dict:
        """Send a GraphQL request to delete a project model."""
        payload = map_delete_project_model_input(project_model_id)
        mutation = get_delete_project_model_mutation()
        result = self.graphql_client.execute(mutation, payload)
        return result["deleteProjectModel"]

    def list_project_models(
        self,
        filters: ProjectModelFilters,
        fields: ListOrTuple[str],
        options: Optional[QueryOptions] = None,
    ) -> Generator[Dict, None, None]:
        """List project models with given options."""
        fragment = fragment_builder(fields)
        query = get_project_models_query(fragment)
        where = project_model_where_mapper(filters)
        return PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query,
            where,
            options if options else QueryOptions(disable_tqdm=False),
            "Retrieving project models",
            None,
        )
