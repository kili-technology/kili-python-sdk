"""Mixin extending Kili API Gateway class with Asset related operations."""

from collections.abc import Generator

from kili.adapters.kili_api_gateway.asset.formatters import (
    load_asset_json_fields,
)
from kili.adapters.kili_api_gateway.asset.mappers import asset_where_mapper
from kili.adapters.kili_api_gateway.asset.operations import (
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
from kili.adapters.kili_api_gateway.project.common import get_project
from kili.core.graphql.operations.asset.mutations import GQL_SET_ASSET_CONSENSUS
from kili.domain.asset import AssetFilters
from kili.domain.types import ListOrTuple


class AssetOperationMixin(BaseOperationMixin):
    """Mixin extending Kili API Gateway class with Assets related operations."""

    def list_assets(
        self,
        filters: AssetFilters,
        fields: ListOrTuple[str],
        options: QueryOptions,
    ) -> Generator[dict, None, None]:
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
        self,
        filters: AssetFilters,
        fields: ListOrTuple[str],
        options: QueryOptions,
        project_info,
    ) -> Generator[dict, None, None]:
        """List assets with given options."""
        assets_batch_max_amount = 10 if project_info["inputType"] == "VIDEO" else 50
        batch_size_to_use = min(options.batch_size, assets_batch_max_amount)

        options = QueryOptions(options.disable_tqdm, options.first, options.skip, batch_size_to_use)

        required_fields = {"content", "jsonContent", "resolution.width", "resolution.height"}
        if "labels.jsonResponse" in fields:
            required_fields.add("labels.jsonResponseUrl")
        if "latestLabel.jsonResponse" in fields:
            required_fields.add("latestLabel.jsonResponseUrl")
        fields = list(fields)
        for field in required_fields:
            if field not in fields:
                fields.append(field)

        fragment = fragment_builder(fields)
        query = get_assets_query(fragment)
        where = asset_where_mapper(filters)
        assets_gen = PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, "Retrieving assets", GQL_COUNT_ASSETS
        )
        assets_gen = (
            load_asset_json_fields(asset, fields, self.http_client) for asset in assets_gen
        )

        yield from assets_gen

    def count_assets(self, filters: AssetFilters) -> int:
        """Send a GraphQL request calling countIssues resolver."""
        where = asset_where_mapper(filters)
        payload = {"where": where}
        count_result = self.graphql_client.execute(GQL_COUNT_ASSETS, payload)
        count: int = count_result["data"]
        return count

    def create_upload_bucket_signed_urls(self, file_paths: list[str]) -> list[str]:
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

    def update_asset_consensus(
        self,
        project_id: str,
        is_consensus: bool,
        asset_id: str | None = None,
        external_id: str | None = None,
    ) -> bool:
        """Update consensus on an asset."""
        if asset_id is None and external_id is None:
            raise ValueError("At least one of asset_id or external_id must be provided")

        payload = {
            "projectId": project_id,
            "isConsensus": is_consensus,
        }
        if asset_id is not None:
            payload["assetId"] = asset_id
        if external_id is not None:
            payload["externalId"] = external_id

        result = self.graphql_client.execute(GQL_SET_ASSET_CONSENSUS, payload)
        return result["data"]
