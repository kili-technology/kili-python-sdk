"""Module for testing the user-facing-queries method"""


from typing import Dict, Generator, List
from unittest.mock import MagicMock, patch

import pytest
from typeguard import check_type

from kili.graphql.operations.asset.queries import AssetQuery
from kili.graphql.operations.user.queries import UserQuery
from kili.queries.asset import QueriesAsset
from kili.queries.user import QueriesUser


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
def test_users_query_return_type(mock, args, kwargs, expected_return_type):
    auth = MagicMock()
    kili = QueriesUser(auth)

    result = kili.users(*args, **kwargs)
    assert check_type("result", result, expected_return_type) is None


@pytest.mark.parametrize(
    "args, kwargs, expected_return_type",
    [
        (("project-id",), {}, List[Dict]),
        (("project-id",), {"as_generator": False}, List[Dict]),
        (("project-id",), {"as_generator": True}, Generator[Dict, None, None]),
        ((), {"project_id": "project-id"}, List[Dict]),
        ((), {"project_id": "project-id", "as_generator": True}, Generator[Dict, None, None]),
        ((), {"project_id": "project-id", "as_generator": False}, List[Dict]),
    ],
)
@patch.object(AssetQuery, "__call__")
def test_assets_query_return_type(mock, args, kwargs, expected_return_type):
    auth = MagicMock()
    kili = QueriesAsset(auth)

    result = kili.assets(*args, **kwargs)
    assert check_type("result", result, expected_return_type) is None
