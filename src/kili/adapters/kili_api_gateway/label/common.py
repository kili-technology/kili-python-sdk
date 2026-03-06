"""Label gateway common."""

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.asset.formatters import load_asset_json_fields
from kili.adapters.kili_api_gateway.asset.operations import get_assets_query
from kili.adapters.kili_api_gateway.helpers.queries import fragment_builder
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.asset.asset import AssetId
from kili.domain.types import ListOrTuple
from kili.exceptions import NotFound


def get_asset(
    graphql_client: GraphQLClient,
    http_client: HttpClient,
    asset_id: AssetId,
    fields: ListOrTuple[str],
) -> dict:
    """Get asset."""
    fragment = fragment_builder(fields)
    query = get_assets_query(fragment)
    result = graphql_client.execute(
        query=query, variables={"where": {"id": asset_id}, "first": 1, "skip": 0}
    )
    assets = result["data"]

    if len(assets) == 0:
        raise NotFound(
            f"asset ID: {asset_id}. The asset does not exist or you do not have access to it."
        )
    return load_asset_json_fields(assets[0], fields, http_client=http_client)
