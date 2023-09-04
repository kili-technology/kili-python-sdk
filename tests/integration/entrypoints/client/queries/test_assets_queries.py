from typing import Dict, Generator, List
from unittest.mock import patch

import pytest
from typeguard import check_type

from kili.core.graphql.operations.asset.queries import AssetQuery
from kili.entrypoints.queries.asset import QueriesAsset


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
def test_assets_query_return_type(mocker, args, kwargs, expected_return_type):
    kili = QueriesAsset()
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()

    result = kili.assets(*args, **kwargs)
    assert check_type("result", result, expected_return_type) is None
