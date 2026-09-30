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


# Removed in LAB-4756, each with the filter that replaces it
REMOVED_FILTERS = {
    "consensus_mark_gt": ("consensus_mark_gte", 0.1),
    "consensus_mark_lt": ("consensus_mark_lte", 0.9),
    "honeypot_mark_gt": ("honeypot_mark_gte", 0.1),
    "honeypot_mark_lt": ("honeypot_mark_lte", 0.9),
    "label_consensus_mark_gt": ("label_consensus_mark_gte", 0.1),
    "label_consensus_mark_lt": ("label_consensus_mark_lte", 0.9),
    "label_created_at_gt": ("label_created_at_gte", "2020-01-01"),
    "label_created_at_lt": ("label_created_at_lte", "2020-01-01"),
    "label_honeypot_mark_gt": ("label_honeypot_mark_gte", 0.1),
    "label_honeypot_mark_lt": ("label_honeypot_mark_lte", 0.9),
    "external_id_contains": ("external_id_strictly_in", ["asset-a"]),
}


@pytest.mark.parametrize("method", ["assets", "count_assets"])
@pytest.mark.parametrize("removed_filter", REMOVED_FILTERS)
def test_assets_queries_reject_removed_filters(kili_api_gateway, method, removed_filter):
    asset_client_methods = AssetClientMethods()
    asset_client_methods.kili_api_gateway = kili_api_gateway
    value = REMOVED_FILTERS[removed_filter][1]

    with pytest.raises(TypeError, match=removed_filter):
        getattr(asset_client_methods, method)(project_id="project-id", **{removed_filter: value})


@pytest.mark.parametrize(("replacement", "value"), REMOVED_FILTERS.values())
def test_count_assets_passes_replacement_filters_through(kili_api_gateway, replacement, value):
    kili_api_gateway.count_assets.return_value = 0
    asset_client_methods = AssetClientMethods()
    asset_client_methods.kili_api_gateway = kili_api_gateway

    asset_client_methods.count_assets(project_id="project-id", **{replacement: value})

    filters = kili_api_gateway.count_assets.call_args[0][0]
    assert getattr(filters, replacement) == value


@pytest.mark.parametrize(("replacement", "value"), REMOVED_FILTERS.values())
def test_assets_passes_replacement_filters_through(kili_api_gateway, replacement, value):
    kili_api_gateway.list_assets.return_value = iter([])
    kili_api_gateway.get_project.return_value = {"steps": [], "workflowVersion": "V1"}
    asset_client_methods = AssetClientMethods()
    asset_client_methods.kili_api_gateway = kili_api_gateway

    asset_client_methods.assets(project_id="project-id", **{replacement: value})

    filters = kili_api_gateway.list_assets.call_args[0][0]
    assert getattr(filters, replacement) == value
