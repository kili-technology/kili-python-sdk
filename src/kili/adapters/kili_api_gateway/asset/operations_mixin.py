"""Mixin extending Kili API Gateway class with Asset related operations."""

from typing import Dict, Generator, List

from kili.adapters.kili_api_gateway.asset.formatters import (
    load_asset_json_fields,
)
from kili.adapters.kili_api_gateway.asset.mappers import asset_where_mapper
from kili.adapters.kili_api_gateway.asset.operations import (
    GQL_COUNT_ASSETS,
    GQL_CREATE_UPLOAD_BUCKET_SIGNED_URLS,
    get_assets_query,
)
from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.adapters.kili_api_gateway.label.annotation_to_json_response import (
    AnnotationsToJsonResponseConverter,
)
from kili.domain.asset import AssetFilters
from kili.domain.types import ListOrTuple


class AssetOperationMixin(BaseOperationMixin):
    """Mixin extending Kili API Gateway class with Assets related operations."""

    def list_assets(
        self,
        filters: AssetFilters,
        fields: ListOrTuple[str],
        options: QueryOptions,
    ) -> Generator[Dict, None, None]:
        """List assets with given options."""
        added_label_id_field = added_latest_label_id_field = False
        if "labels.jsonResponse" in fields and "labels.id" not in fields:
            fields = (*fields, "labels.id")
            added_label_id_field = True
        if "latestLabel.jsonResponse" in fields and "latestLabel.id" not in fields:
            fields = (*fields, "latestLabel.id")
            added_latest_label_id_field = True

        fragment = fragment_builder(fields)
        query = get_assets_query(fragment)
        where = asset_where_mapper(filters)
        assets_gen = PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, "Retrieving assets", GQL_COUNT_ASSETS
        )
        assets_gen = (load_asset_json_fields(asset, fields) for asset in assets_gen)

        if any("jsonResponse" in field for field in fields):
            converter = AnnotationsToJsonResponseConverter(
                graphql_client=self.graphql_client, project_id=filters.project_id
            )
            for asset in assets_gen:
                if "latestLabel.jsonResponse" in fields and asset.get("latestLabel"):
                    converter.patch_label_json_response(
                        asset["latestLabel"], asset["latestLabel"]["id"]
                    )
                    if added_latest_label_id_field:
                        asset["latestLabel"].pop("id")
                if "labels.jsonResponse" in fields:
                    for label in asset.get("labels", []):
                        converter.patch_label_json_response(label, label["id"])
                        if added_label_id_field:
                            label.pop("id")

                yield asset

        else:
            yield from assets_gen

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
