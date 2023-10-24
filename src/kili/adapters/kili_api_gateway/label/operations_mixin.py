"""Mixin extending Kili API Gateway class with label related operations."""

from typing import Dict, Generator, List, Optional

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.core.utils.pagination import BatchIteratorBuilder
from kili.domain.label import LabelFilters, LabelId
from kili.domain.types import ListOrTuple
from kili.utils.tqdm import tqdm

from .formatters import load_label_json_fields
from .mappers import label_where_mapper, update_label_data_mapper
from .operations import (
    GQL_COUNT_LABELS,
    GQL_DELETE_LABELS,
    get_labels_query,
    get_update_properties_in_label_query,
)
from .types import UpdateLabelData


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
        labels_gen = PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, "Retrieving labels", GQL_COUNT_LABELS
        )
        return (load_label_json_fields(label, fields) for label in labels_gen)

    def update_properties_in_label(
        self, label_id: LabelId, data: UpdateLabelData, fields: ListOrTuple[str]
    ) -> Dict:
        """Update properties in label."""
        fragment = fragment_builder(fields)
        query = get_update_properties_in_label_query(fragment)
        variables = {"where": {"id": label_id}, "data": update_label_data_mapper(data)}
        result = self.graphql_client.execute(query, variables)
        modified_label = result["data"]
        return load_label_json_fields(modified_label, fields=fields)

    def delete_labels(
        self, ids: ListOrTuple[LabelId], disable_tqdm: Optional[bool]
    ) -> List[LabelId]:
        """Delete labels."""
        delete_label_ids: List[LabelId] = []

        with tqdm(total=len(ids), desc="Deleting labels", disable=disable_tqdm) as pbar:
            for batch_of_label_ids in BatchIteratorBuilder(ids):
                variables = {"ids": batch_of_label_ids}
                result = self.graphql_client.execute(GQL_DELETE_LABELS, variables)
                batch_deleted_label_ids = result["data"]
                delete_label_ids.extend(batch_deleted_label_ids)
                pbar.update(len(batch_of_label_ids))

        return delete_label_ids
