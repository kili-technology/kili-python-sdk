"""Base class for entrypoints dealing with GraphQL operations."""

import abc
from typing import List, Optional, Type, TypeVar, cast

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.core.graphql.graphql_client import GraphQLClient
from kili.core.helpers import format_result
from kili.domain.asset import AssetExternalId, AssetId
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.use_cases.asset.utils import AssetUseCasesUtils

T = TypeVar("T")


class BaseOperationEntrypointMixin(abc.ABC):
    """Base class for entrypoints dealing with GraphQL operations."""

    # FIXME: graphql_client and http_client should be removed once
    # all methods have been moved to the new architecture
    graphql_client: GraphQLClient
    http_client: HttpClient
    kili_api_gateway: KiliAPIGateway

    def format_result(self, name: str, result: dict, object_: Optional[Type[T]] = None) -> T:
        """Format the result of a graphQL query.

        FIXME: this should not be used at that level.
        """
        return format_result(name, result, object_, self.http_client)

    def _resolve_asset_ids(
        self,
        asset_ids: Optional[List[str]],
        external_ids: Optional[List[str]],
        project_id: Optional[str],
    ) -> ListOrTuple[AssetId]:
        # FIXME: temporary method to be removed once all methods have been
        # moved to the new architecture
        return AssetUseCasesUtils(self.kili_api_gateway).get_asset_ids_or_throw_error(
            cast(Optional[List[AssetId]], asset_ids),
            cast(Optional[List[AssetExternalId]], external_ids),
            ProjectId(project_id) if project_id else None,
        )
