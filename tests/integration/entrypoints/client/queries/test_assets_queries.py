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
