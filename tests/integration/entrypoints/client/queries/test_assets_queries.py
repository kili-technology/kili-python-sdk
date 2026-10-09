from collections.abc import Generator

import pytest
from typeguard import check_type

from kili.presentation.client.asset import AssetClientMethods


@pytest.mark.parametrize(
    ("args", "kwargs", "expected_return_type"),
    [
        (("project-id",), {}, list[dict]),
        (("project-id",), {"as_generator": False}, list[dict]),
        (("project-id",), {"as_generator": True}, Generator[dict, None, None]),
        (("project-id",), {"label_output_format": "parsed_label"}, list[dict]),
        (
            ("project-id",),
            {"label_output_format": "parsed_label", "as_generator": True},
            Generator[dict, None, None],
        ),
        ((), {"project_id": "project-id"}, list[dict]),
        ((), {"project_id": "project-id", "as_generator": True}, Generator[dict, None, None]),
        ((), {"project_id": "project-id", "as_generator": False}, list[dict]),
    ],
)
def test_assets_query_return_type(kili_api_gateway, args, kwargs, expected_return_type):
    asset_client_methods = AssetClientMethods()
    kili_api_gateway.list_assets = lambda *args, **kwargs: (a for a in [])
    kili_api_gateway.get_project = lambda *args, **kwargs: {"steps": [], "workflowVersion": "V1"}
    asset_client_methods.kili_api_gateway = kili_api_gateway
    result = asset_client_methods.assets(*args, **kwargs)
    check_type(result, expected_return_type)


FILTERS_PASSED_THROUGH = [
    ("consensus_mark_gte", 0.1),
    ("consensus_mark_lte", 0.9),
    ("honeypot_mark_gte", 0.1),
    ("honeypot_mark_lte", 0.9),
    ("label_consensus_mark_gte", 0.1),
    ("label_consensus_mark_lte", 0.9),
    ("label_created_at_gte", "2020-01-01"),
    ("label_created_at_lte", "2020-01-01"),
    ("label_honeypot_mark_gte", 0.1),
    ("label_honeypot_mark_lte", 0.9),
    ("external_id_strictly_in", ["asset-a"]),
]


@pytest.mark.parametrize(("filter_name", "value"), FILTERS_PASSED_THROUGH)
def test_count_assets_passes_filters_through(kili_api_gateway, filter_name, value):
    kili_api_gateway.count_assets.return_value = 0
    asset_client_methods = AssetClientMethods()
    asset_client_methods.kili_api_gateway = kili_api_gateway

    asset_client_methods.count_assets(project_id="project-id", **{filter_name: value})

    filters = kili_api_gateway.count_assets.call_args[0][0]
    assert getattr(filters, filter_name) == value


@pytest.mark.parametrize(("filter_name", "value"), FILTERS_PASSED_THROUGH)
def test_assets_passes_filters_through(kili_api_gateway, filter_name, value):
    kili_api_gateway.list_assets.return_value = iter([])
    kili_api_gateway.get_project.return_value = {"steps": [], "workflowVersion": "V1"}
    asset_client_methods = AssetClientMethods()
    asset_client_methods.kili_api_gateway = kili_api_gateway

    asset_client_methods.assets(project_id="project-id", **{filter_name: value})

    filters = kili_api_gateway.list_assets.call_args[0][0]
    assert getattr(filters, filter_name) == value
