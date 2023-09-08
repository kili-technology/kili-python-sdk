"""Base class for all KiliAPIGateway Operation Mixin classes."""
from abc import ABC
from itertools import chain
from typing import Dict, Generator, List, Literal, Optional

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.asset.mappers import asset_where_mapper
from kili.adapters.kili_api_gateway.asset.operations import (
    GQL_COUNT_ASSETS,
    get_assets_query,
)
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.core.graphql.graphql_client import GraphQLClient
from kili.core.utils import pagination
from kili.domain.asset import AssetExternalId, AssetFilters, AssetId
from kili.domain.project import ProjectId
from kili.exceptions import NotFound


class BaseOperationMixin(ABC):
    """Base class for all KiliAPIGateway Operation Mixin classes.

    It is used to share the GraphQL client between all methods classes.

    It is not meant to be used and instantiated directly.
    """

    graphql_client: GraphQLClient  # instantiated in the KiliAPIGateway child class
    http_client: HttpClient  # instantiated in the KiliAPIGateway child class

    def _get_asset_ids_or_throw_error(
        self,
        asset_ids: Optional[List[AssetId]],
        external_ids: Optional[List[AssetExternalId]],
        project_id: Optional[ProjectId],
    ) -> List[AssetId]:
        """Check if external id to internal id conversion is valid and needed."""

        if asset_ids is None:
            assert external_ids
            assert project_id
            id_map = self._infer_ids_from_external_ids(external_ids, project_id)
            asset_ids = [id_map[id] for id in external_ids]

        return asset_ids

    def _infer_ids_from_external_ids(
        self, external_ids: List[AssetExternalId], project_id: ProjectId
    ) -> Dict[AssetExternalId, AssetId]:
        """Infer asset ids from external ids."""
        id_map = self._build_id_map(external_ids, project_id)

        if len(id_map) < len(set(external_ids)):
            assets_not_found = [
                external_id for external_id in external_ids if external_id not in id_map
            ]
            raise NotFound(
                f"The assets whose external_id are: {assets_not_found} have not been found in the"
                f" project of Id {project_id}"
            )
        if len(id_map) > len(set(external_ids)):
            raise NotFound(
                "Several assets have been found for the same external_id. Please consider using"
                " asset ids instead."
            )
        return id_map

    def _build_id_map(
        self, asset_external_ids: List[AssetExternalId], project_id: ProjectId
    ) -> Dict[AssetExternalId, AssetId]:
        # query all assets by external ids batches when there are too many
        assets_generators = []
        for external_ids_batch in pagination.BatchIteratorBuilder(asset_external_ids, 1000):
            assets_generators.append(self._get_asset_ids_from(project_id, external_ids_batch))
        assets = chain(*assets_generators)
        id_map: Dict[AssetExternalId, AssetId] = {}
        asset_external_ids_set = set(asset_external_ids)
        for asset in (asset for asset in assets if asset["externalId"] in asset_external_ids_set):
            id_map[asset["externalId"]] = asset["id"]
        return id_map

    def _get_asset_ids_from(
        self,
        project_id: ProjectId,
        asset_external_ids: List[AssetExternalId],
    ) -> Generator[Dict[Literal["id", "externalId"], str], None, None]:
        """List assets with given options."""
        fragment = fragment_builder(["id", "externalId"])
        query = get_assets_query(fragment)
        where = asset_where_mapper(
            AssetFilters(project_id, external_id_strictly_in=[str(e) for e in asset_external_ids])
        )
        query_options = QueryOptions(disable_tqdm=True)

        return PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, query_options, "", GQL_COUNT_ASSETS
        )
