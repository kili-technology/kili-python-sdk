"""Mixin extending Kili API Gateway class with Asset related operations."""

from typing import Dict, Generator, List

from kili_formats.tool.annotations_to_json_response import (
    AnnotationsToJsonResponseConverter,
)

from kili.adapters.kili_api_gateway.asset.formatters import (
    load_asset_json_fields,
)
from kili.adapters.kili_api_gateway.asset.mappers import asset_where_mapper
from kili.adapters.kili_api_gateway.asset.operations import (
    GQL_COUNT_ASSET_ANNOTATIONS,
    GQL_COUNT_ASSETS,
    GQL_CREATE_UPLOAD_BUCKET_SIGNED_URLS,
    GQL_FILTER_EXISTING_ASSETS,
    get_assets_query,
)
from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.adapters.kili_api_gateway.label.common import get_annotation_fragment
from kili.adapters.kili_api_gateway.project.common import get_project
from kili.domain.asset import AssetFilters
from kili.domain.types import ListOrTuple

# Threshold for batching based on number of annotations
# This is used to determine whether to use a single batch or multiple batches
# when fetching assets. If the number of annotations counted exceeds this threshold,
# the asset fetch will be done in multiple smaller batches to avoid performance issues.
THRESHOLD_FOR_BATCHING = 200


class AssetOperationMixin(BaseOperationMixin):
    """Mixin extending Kili API Gateway class with Assets related operations."""

    def list_assets(
        self,
        filters: AssetFilters,
        fields: ListOrTuple[str],
        options: QueryOptions,
    ) -> Generator[Dict, None, None]:
        """List assets with given options."""
        if "labels.jsonResponse" in fields or "latestLabel.jsonResponse" in fields:
            # Check if we can get the jsonResponse of if we need to rebuild it.
            project_info = get_project(
                self.graphql_client, filters.project_id, ("inputType", "jsonInterface")
            )
            if project_info["inputType"] in {
                "VIDEO",
                "LLM_RLHF",
                "LLM_INSTR_FOLLOWING",
                "LLM_STATIC",
                "GEOSPATIAL",
            }:
                yield from self.list_assets_split(filters, fields, options, project_info)
                return

        fragment = fragment_builder(fields)
        query = get_assets_query(fragment)
        where = asset_where_mapper(filters)
        assets_gen = PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query,
            where,
            options,
            "Retrieving assets",
            GQL_COUNT_ASSETS,
            "id" if "id" in fields else None,
        )
        assets_gen = (
            load_asset_json_fields(asset, fields, self.http_client) for asset in assets_gen
        )

        yield from assets_gen

    def list_assets_split(
        self, filters: AssetFilters, fields: ListOrTuple[str], options: QueryOptions, project_info
    ) -> Generator[Dict, None, None]:
        """List assets with given options."""
        nb_annotations = self.count_assets_annotations(filters)
        assets_batch_max_amount = 10 if project_info["inputType"] == "VIDEO" else 50
        batch_size_to_use = min(options.batch_size, assets_batch_max_amount)
        batch_size = (
            1 if nb_annotations / batch_size_to_use > THRESHOLD_FOR_BATCHING else batch_size_to_use
        )

        options = QueryOptions(options.disable_tqdm, options.first, options.skip, batch_size)

        inner_annotation_fragment = get_annotation_fragment()
        annotation_fragment = f"""
            annotations {{
                {inner_annotation_fragment}
            }}
        """
        # Ensure 'content', 'resolution', and 'jsonContent' are present in fields
        required_fields = {"content", "jsonContent", "resolution.width", "resolution.height"}
        fields = list(fields)
        for field in required_fields:
            if field not in fields:
                fields.append(field)

        fragment = fragment_builder(
            fields, {"labels": annotation_fragment, "latestLabel": annotation_fragment}
        )
        query = get_assets_query(fragment)
        where = asset_where_mapper(filters)
        assets_gen = PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, "Retrieving assets", GQL_COUNT_ASSETS
        )
        assets_gen = (
            load_asset_json_fields(asset, fields, self.http_client) for asset in assets_gen
        )
        converter = AnnotationsToJsonResponseConverter(
            json_interface=project_info["jsonInterface"],
            project_input_type=project_info["inputType"],
        )
        is_requesting_annotations = any("annotations." in element for element in fields)
        for asset in assets_gen:
            if "latestLabel.jsonResponse" in fields and asset.get("latestLabel"):
                converter.patch_label_json_response(
                    asset, asset["latestLabel"], asset["latestLabel"]["annotations"]
                )
                if not is_requesting_annotations:
                    asset["latestLabel"].pop("annotations")

            if "labels.jsonResponse" in fields:
                for label in asset.get("labels", []):
                    converter.patch_label_json_response(asset, label, label["annotations"])
                    if not is_requesting_annotations:
                        label.pop("annotations")
            yield asset

    def count_assets(self, filters: AssetFilters) -> int:
        """Send a GraphQL request calling countIssues resolver."""
        where = asset_where_mapper(filters)
        payload = {"where": where}
        count_result = self.graphql_client.execute(GQL_COUNT_ASSETS, payload)
        count: int = count_result["data"]
        return count

    def create_upload_bucket_signed_urls(self, file_paths: List[str]) -> List[str]:
        """Send a GraphQL request calling createUploadBucketSignedUrls resolver."""
        payload = {
            "filePaths": file_paths,
        }
        urls_response = self.graphql_client.execute(GQL_CREATE_UPLOAD_BUCKET_SIGNED_URLS, payload)
        return urls_response["urls"]

    def filter_existing_assets(self, project_id: str, assets_external_ids: ListOrTuple[str]):
        """Send a GraphQL request calling filterExistingAssets resolver."""
        payload = {
            "projectID": project_id,
            "externalIDs": assets_external_ids,
        }
        external_id_response = self.graphql_client.execute(GQL_FILTER_EXISTING_ASSETS, payload)
        return external_id_response["external_ids"]

    def count_assets_annotations(self, filters: AssetFilters) -> int:
        """Count the number of annotations for assets matching the filters."""
        where = asset_where_mapper(filters)
        payload = {"where": where}
        count_result = self.graphql_client.execute(GQL_COUNT_ASSET_ANNOTATIONS, payload)
        count: int = count_result["data"]
        return count
