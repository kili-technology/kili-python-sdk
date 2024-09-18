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
    map_delete_model_input,
    organization_model_where_wrapper,
    project_model_where_mapper,
)
from kili.adapters.kili_api_gateway.model_configuration.operations import (
    get_create_model_mutation,
    get_delete_model_mutation,
    get_organization_models_query,
    get_project_models_query,
)
from kili.domain.project_model import (
    ModelToCreateInput,
    OrganizationModelFilters,
    ProjectModelFilters,
)
from kili.domain.types import ListOrTuple


class ModelConfigurationOperationMixin(BaseOperationMixin):
    """Mixin extending Kili API Gateway class with model configuration related operations."""

    def list_organization_models(
        self,
        filters: OrganizationModelFilters,
        fields: ListOrTuple[str],
        options: Optional[QueryOptions] = None,
    ) -> Generator[Dict, None, None]:
        """List models with given options."""
        fragment = fragment_builder(fields)
        query = get_organization_models_query(fragment)
        where = organization_model_where_wrapper(filters)
        return PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query,
            where,
            options if options else QueryOptions(disable_tqdm=False),
            "Retrieving organization models",
            None,
        )

    def create_model(self, model: ModelToCreateInput):
        """Send a GraphQL request calling createModel resolver."""
        payload = {"input": map_create_model_input(model)}
        fragment = fragment_builder(["id"])
        mutation = get_create_model_mutation(fragment)
        result = self.graphql_client.execute(mutation, payload)
        return result["createModel"]

    def delete_model(self, model_id: str):
        """Send a GraphQL request to delete an organization model."""
        payload = map_delete_model_input(model_id)
        mutation = get_delete_model_mutation()
        result = self.graphql_client.execute(mutation, payload)
        return result["deleteModel"]

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
