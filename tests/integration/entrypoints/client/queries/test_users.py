from typing import Dict, Generator, List
from unittest.mock import patch

import pytest
from typeguard import check_type

from kili.core.graphql.operations.user.queries import UserQuery
from kili.entrypoints.queries.user import QueriesUser


@pytest.mark.parametrize(
    ("args", "kwargs", "expected_return_type"),
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
