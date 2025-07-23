from typing import Dict, Generator, List

import pytest
from typeguard import check_type

from kili.presentation.client.asset import AssetClientMethods


@pytest.mark.parametrize(
    ("args", "kwargs", "expected_return_type"),
    [
        (("project-id",), {}, List[Dict]),
        (("project-id",), {"as_generator": False}, List[Dict]),
        (("project-id",), {"as_generator": True}, Generator[Dict, None, None]),
        (("project-id",), {"label_output_format": "parsed_label"}, List[Dict]),
        (
            ("project-id",),
            {"label_output_format": "parsed_label", "as_generator": True},
            Generator[Dict, None, None],
        ),
        ((), {"project_id": "project-id"}, List[Dict]),
        ((), {"project_id": "project-id", "as_generator": True}, Generator[Dict, None, None]),
        ((), {"project_id": "project-id", "as_generator": False}, List[Dict]),
    ],
)
def test_assets_query_return_type(kili_api_gateway, args, kwargs, expected_return_type):
    asset_client_methods = AssetClientMethods()
    kili_api_gateway.list_assets = lambda *args, **kwargs: (a for a in [])
    kili_api_gateway.get_project = lambda *args, **kwargs: {"steps": [], "workflowVersion": "V1"}
    asset_client_methods.kili_api_gateway = kili_api_gateway
    result = asset_client_methods.assets(*args, **kwargs)
    check_type(result, expected_return_type)
