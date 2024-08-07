"""Mixin extending Kili API Gateway class with Api Keys related operations."""

from typing import Dict, Generator, Optional

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.adapters.kili_api_gateway.model_configuration.mappers import project_model_where_mapper
from kili.adapters.kili_api_gateway.model_configuration.operations import get_project_models_query
from kili.domain.project_model import ProjectModelFilters
from kili.domain.types import ListOrTuple


class ModelConfigurationOperationMixin(BaseOperationMixin):
    """Mixin extending Kili API Gateway class with model configuration related operations."""

    def list_project_models(
        self,
        filters: ProjectModelFilters,
        fields: ListOrTuple[str],
        options: Optional[QueryOptions] = None,
    ) -> Generator[Dict, None, None]:
        """List assets with given options."""
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
