"""Module for testing the user-facing-queries method."""


from typing import Dict, Generator, List
from unittest.mock import MagicMock, patch

import pytest
from typeguard import check_type

from kili.core.graphql.operations.user.queries import UserQuery
from kili.entrypoints.queries.user import QueriesUser
from kili.presentation.client.asset import AssetClientMethods


@pytest.mark.parametrize(
    "args, kwargs, expected_return_type",
    [
        ((), {}, List[Dict]),
        ((), {"as_generator": True}, Generator[Dict, None, None]),
        ((), {"as_generator": False}, List[Dict]),
        ((), {"email": "test@kili.com", "as_generator": False}, List[Dict]),
    ],
)
@patch.object(UserQuery, "__call__")
def test_users_query_return_type(mocker, args, kwargs, expected_return_type):
    kili = QueriesUser()
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()

    result = kili.users(*args, **kwargs)
    assert check_type("result", result, expected_return_type) is None


@pytest.mark.parametrize(
    "args, kwargs, expected_return_type",
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
    asset_client_methods.kili_api_gateway = MagicMock()
    result = asset_client_methods.assets(*args, **kwargs)
    assert check_type("result", result, expected_return_type) is None
