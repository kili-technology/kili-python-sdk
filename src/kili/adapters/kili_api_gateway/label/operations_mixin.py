"""Mixin extending Kili API Gateway class with label related operations."""

from typing import Dict, Generator

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.domain.label import LabelFilters
from kili.domain.types import ListOrTuple

from .mappers import label_where_mapper
from .operations import GQL_COUNT_LABELS, get_labels_query


class LabelOperationMixin(BaseOperationMixin):
    """Mixin extending Kili API Gateway class with label related operations."""

    def count_labels(self, filters: LabelFilters) -> int:
        """Count labels."""
        variables = {"where": label_where_mapper(filters)}
        result = self.graphql_client.execute(GQL_COUNT_LABELS, variables)
        return result["data"]

    def list_labels(
        self,
        filters: LabelFilters,
        fields: ListOrTuple[str],
        options: QueryOptions,
    ) -> Generator[Dict, None, None]:
        """List labels."""
        fragment = fragment_builder(fields)
        query = get_labels_query(fragment)
        where = label_where_mapper(filters)
        return PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, "Retrieving labels", GQL_COUNT_LABELS
        )
