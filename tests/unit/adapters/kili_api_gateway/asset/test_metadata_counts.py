"""Tests for the metadata count operations of the asset gateway."""

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.asset.operations import (
    GQL_COUNT_ASSETS_BY_METADATA_VALUE,
    GQL_LIST_ASSETS_METADATA_KEYS,
)
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.asset import AssetFilters
from kili.domain.project import ProjectId


def test_list_assets_metadata_keys_sends_the_asset_where(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    graphql_client.execute.return_value = {"data": ["camera", "split"]}
    gateway = KiliAPIGateway(graphql_client, http_client)

    keys = gateway.list_assets_metadata_keys(
        AssetFilters(project_id=ProjectId("project_id"), status_in=["LABELED"])
    )

    assert keys == ["camera", "split"]
    query, payload = graphql_client.execute.call_args.args
    assert query == GQL_LIST_ASSETS_METADATA_KEYS
    assert payload["where"]["project"] == {"id": "project_id"}
    assert payload["where"]["statusIn"] == ["LABELED"]


def test_count_assets_by_metadata_value_maps_the_counts_to_snake_case(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    graphql_client.execute.return_value = {
        "data": {
            "values": [{"value": 3, "count": 2}, {"value": True, "count": 1}],
            "missingCount": 4,
        }
    }
    gateway = KiliAPIGateway(graphql_client, http_client)

    counts = gateway.count_assets_by_metadata_value(
        AssetFilters(project_id=ProjectId("project_id"), metadata_where={"split": "train"}),
        "camera",
    )

    assert counts == {
        "values": [{"value": 3, "count": 2}, {"value": True, "count": 1}],
        "missing_count": 4,
    }
    query, payload = graphql_client.execute.call_args.args
    assert query == GQL_COUNT_ASSETS_BY_METADATA_VALUE
    assert payload["metadataKey"] == "camera"
    assert payload["where"]["metadata"] == {"split": "train"}


def test_count_assets_by_metadata_value_reads_null_values_as_empty(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    graphql_client.execute.return_value = {"data": {"values": None, "missingCount": 7}}
    gateway = KiliAPIGateway(graphql_client, http_client)

    counts = gateway.count_assets_by_metadata_value(
        AssetFilters(project_id=ProjectId("project_id")), "camera"
    )

    assert counts == {"values": [], "missing_count": 7}
