"""Tests for the metadata count methods of the legacy client."""

import pytest
from typeguard import TypeCheckError

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.asset import AssetFilters
from kili.presentation.client.asset import AssetClientMethods
from kili.utils.logcontext import LogContext


@pytest.fixture()
def client(kili_api_gateway: KiliAPIGateway) -> AssetClientMethods:
    methods = AssetClientMethods()
    methods.kili_api_gateway = kili_api_gateway
    return methods


def test_count_assets_per_metadata_value_builds_the_filters_of_count_assets(
    client: AssetClientMethods, kili_api_gateway: KiliAPIGateway
):
    kili_api_gateway.count_assets_by_metadata_value.return_value = {
        "values": [{"value": "front", "count": 2}],
        "missing_count": 1,
    }

    counts = client.count_assets_per_metadata_value(
        project_id="project_id",
        metadata_key="camera",
        filter={"external_id_strictly_in": ["a", "b"], "metadata_where": {"split": "train"}},
    )

    assert counts == {"values": [{"value": "front", "count": 2}], "missing_count": 1}
    filters, metadata_key = kili_api_gateway.count_assets_by_metadata_value.call_args.args
    assert isinstance(filters, AssetFilters)
    assert filters.project_id == "project_id"
    assert filters.external_id_strictly_in == ["a", "b"]
    assert filters.metadata_where == {"split": "train"}
    assert metadata_key == "camera"


def test_count_assets_per_metadata_value_resolves_step_names_like_count_assets(
    client: AssetClientMethods, kili_api_gateway: KiliAPIGateway
):
    kili_api_gateway.get_project.return_value = {
        "steps": [{"id": "review-step-id", "name": "Review"}],
        "workflowVersion": "V2",
    }
    kili_api_gateway.count_assets_by_metadata_value.return_value = {
        "values": [],
        "missing_count": 0,
    }

    client.count_assets_per_metadata_value(
        project_id="project_id", metadata_key="camera", filter={"step_name_in": ["Review"]}
    )

    filters, _ = kili_api_gateway.count_assets_by_metadata_value.call_args.args
    assert filters.step_id_in == ["review-step-id"]


def test_list_asset_metadata_keys_without_filter_reads_the_whole_project(
    client: AssetClientMethods, kili_api_gateway: KiliAPIGateway
):
    kili_api_gateway.list_assets_metadata_keys.return_value = ["camera", "split"]

    keys = client.list_asset_metadata_keys(project_id="project_id")

    assert keys == ["camera", "split"]
    (filters,) = kili_api_gateway.list_assets_metadata_keys.call_args.args
    assert filters == AssetFilters(project_id="project_id")


def test_an_unknown_filter_key_is_refused(client: AssetClientMethods):
    with pytest.raises(TypeError, match="no_such_filter"):
        client.list_asset_metadata_keys(project_id="project_id", filter={"no_such_filter": 1})


def test_a_filter_value_of_the_wrong_type_is_refused_like_in_count_assets(
    client: AssetClientMethods,
):
    with pytest.raises(TypeCheckError):
        client.count_assets_per_metadata_value(
            project_id="project_id", metadata_key="camera", filter={"status_in": "LABELED"}
        )


@pytest.mark.parametrize(
    ("method", "kwargs"),
    [
        ("count_assets", {}),
        ("list_asset_metadata_keys", {}),
        ("count_assets_per_metadata_value", {"metadata_key": "camera"}),
    ],
)
def test_the_request_is_logged_under_the_public_method(
    client: AssetClientMethods, kili_api_gateway: KiliAPIGateway, method: str, kwargs: dict
):
    kili_api_gateway.count_assets_by_metadata_value.return_value = {
        "values": [],
        "missing_count": 0,
    }

    getattr(client, method)(project_id="project_id", **kwargs)

    assert LogContext()["kili-client-method-name"] == method
