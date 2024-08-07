"""Mixin extending Kili API Gateway class with label related operations."""

import json
from typing import Dict, Generator, List, Optional

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.adapters.kili_api_gateway.project.common import get_project
from kili.core.constants import MUTATION_BATCH_SIZE
from kili.core.utils.pagination import batcher
from kili.domain.asset import AssetId
from kili.domain.label import LabelFilters, LabelId
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.utils.tqdm import tqdm

from .annotation_to_json_response import (
    AnnotationsToJsonResponseConverter,
)
from .common import get_annotation_fragment
from .formatters import load_label_json_fields
from .mappers import (
    append_label_data_mapper,
    append_to_labels_data_mapper,
    label_where_mapper,
    update_label_data_mapper,
)
from .operations import (
    GQL_COUNT_LABELS,
    GQL_DELETE_LABELS,
    get_append_many_labels_mutation,
    get_append_to_labels_mutation,
    get_create_honeypot_mutation,
    get_labels_query,
    get_update_properties_in_label_mutation,
)
from .types import AppendManyLabelsData, AppendToLabelsData, UpdateLabelData


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
        if "jsonResponse" in fields:
            project_info = get_project(
                self.graphql_client, filters.project_id, ("inputType", "jsonInterface")
            )
            if project_info["inputType"] in {"VIDEO", "LLM_RLHF", "LLM_INSTR_FOLLOWING"}:
                yield from self.list_labels_split(filters, fields, options, project_info)
                return

        fragment = fragment_builder(fields)
        query = get_labels_query(fragment)
        where = label_where_mapper(filters)
        labels_gen = PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, "Retrieving labels", GQL_COUNT_LABELS
        )
        labels_gen = (load_label_json_fields(label, fields) for label in labels_gen)
        yield from labels_gen

    def list_labels_split(
        self, filters: LabelFilters, fields: ListOrTuple[str], options: QueryOptions, project_info
    ) -> Generator[Dict, None, None]:
        """List labels."""
        if project_info["inputType"] == "VIDEO":
            options = QueryOptions(
                options.disable_tqdm, options.first, options.skip, min(options.batch_size, 20)
            )

        fragment = fragment_builder(fields)
        inner_annotation_fragment = get_annotation_fragment()
        full_fragment = f"""
            {fragment}
            annotations {{
                {inner_annotation_fragment}
            }}
        """
        query = get_labels_query(full_fragment)
        where = label_where_mapper(filters)
        labels_gen = PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, "Retrieving labels", GQL_COUNT_LABELS
        )
        labels_gen = (load_label_json_fields(label, fields) for label in labels_gen)

        if "jsonResponse" in fields:
            converter = AnnotationsToJsonResponseConverter(
                json_interface=project_info["jsonInterface"],
                project_input_type=project_info["inputType"],
            )
            for label in labels_gen:
                converter.patch_label_json_response(label, label["annotations"])
                if "annotations" not in fields:
                    label.pop("annotations")
                yield label

        else:
            yield from labels_gen

    def update_properties_in_label(
        self, label_id: LabelId, data: UpdateLabelData, fields: ListOrTuple[str]
    ) -> Dict:
        """Update properties in label."""
        fragment = fragment_builder(fields)
        query = get_update_properties_in_label_mutation(fragment)
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
            for batch_of_label_ids in batcher(ids, batch_size=MUTATION_BATCH_SIZE):
                variables = {"ids": batch_of_label_ids}
                result = self.graphql_client.execute(GQL_DELETE_LABELS, variables)
                batch_deleted_label_ids = result["data"]
                delete_label_ids.extend(batch_deleted_label_ids)
                pbar.update(len(batch_of_label_ids))

        return delete_label_ids

    def append_many_labels(
        self,
        data: AppendManyLabelsData,
        fields: ListOrTuple[str],
        disable_tqdm: Optional[bool],
        project_id: Optional[ProjectId],
    ) -> List[Dict]:
        """Append many labels."""
        nb_labels_to_add = len(data.labels_data)

        fragment = fragment_builder(fields)
        query = get_append_many_labels_mutation(fragment=fragment)

        added_labels: List[Dict] = []
        with tqdm(total=nb_labels_to_add, desc="Adding labels", disable=disable_tqdm) as pbar:
            for batch_of_label_data in batcher(data.labels_data, batch_size=MUTATION_BATCH_SIZE):
                variables = {
                    "data": {
                        "labelType": data.label_type,
                        "overwrite": data.overwrite,
                        "labelsData": [
                            append_label_data_mapper(label) for label in batch_of_label_data
                        ],
                    },
                    "where": {
                        "idIn": [label.asset_id for label in batch_of_label_data],
                    },
                }
                if project_id is not None:
                    variables["where"]["project"] = {"id": project_id}

                # we increase the timeout because the import can take a long time
                batch_result = self.graphql_client.execute(query, variables, timeout=120)
                added_labels.extend(batch_result["data"])
                pbar.update(len(batch_of_label_data))

        return added_labels

    def append_to_labels(
        self, data: AppendToLabelsData, asset_id: AssetId, fields: ListOrTuple[str]
    ) -> Dict:
        """Append to labels."""
        fragment = fragment_builder(fields)
        query = get_append_to_labels_mutation(fragment)
        variables = {
            "where": {"id": asset_id},
            "data": append_to_labels_data_mapper(data),
        }
        result = self.graphql_client.execute(query, variables)
        return result["data"]

    def create_honeypot_label(
        self, json_response: Dict, asset_id: AssetId, fields: ListOrTuple[str]
    ) -> Dict:
        """Create honeypot label."""
        fragment = fragment_builder(fields)
        query = get_create_honeypot_mutation(fragment)
        variables = {
            "data": {"jsonResponse": json.dumps(json_response)},
            "where": {"id": asset_id},
        }
        result = self.graphql_client.execute(query, variables)
        return result["data"]
