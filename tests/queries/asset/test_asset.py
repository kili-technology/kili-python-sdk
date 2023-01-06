"""
    Tests assets query.
"""
from unittest.mock import MagicMock

import pandas as pd

from kili.queries.asset import QueriesAsset
from tests.utils import mocked_count_method, mocked_query_method

mocked_auth = MagicMock()
mocked_auth.client.endpoint = "https://staging.cloud.kili-technology.com/api/label/v2/graphql-fake"

TEST_CASES = [
    {
        "case": (
            "AAU, When I query assets with first=50 and skip=20, I skip the 20"
            " first assets I get the 50 assets following"
        ),
        "args": {"project_id": "abcdef", "first": 50, "skip": 20, "disable_tqdm": True},
        "expected_result": [{"id": i} for i in range(20, 70)],
        "expected_type": "list",
    },
    {
        "case": (
            "AAU, When I query assets with first=3, skip=20 as_generator=True I get a "
            "generator that skips the 20 first assets and yield the 3 assets following"
        ),
        "args": {"project_id": "abcdef", "as_generator": True, "first": 3, "skip": 20},
        "expected_result": [{"id": i} for i in range(20, 23)],
        "expected_type": "generator",
    },
    {
        "case": (
            'AAU, When I query assets with first=50 with format="pandas", I get the '
            "first 50 assets as a pandas DataFrame"
        ),
        "args": {
            "project_id": "abcdef",
            "format": "pandas",
            "first": 50,
            "disable_tqdm": True,
        },
        "expected_result": [{"id": i} for i in range(50)],
        "expected_type": "DataFrame",
    },
]


def test_assets(mocker):
    """
    Test return type of the assets method
    """
    mocker.patch("kili.queries.asset.QueriesAsset._query_assets", side_effect=mocked_query_method)
    mocker.patch("kili.queries.asset.QueriesAsset.count_assets", return_value=mocked_count_method)
    for test_case in TEST_CASES:
        case_name = test_case["case"]
        expected = test_case["expected_result"]
        actual = QueriesAsset(mocked_auth).assets(**test_case["args"])
        assert (
            type(actual).__name__ == test_case["expected_type"]
        ), f'Test case "{case_name}" failed'
        if isinstance(actual, pd.DataFrame):
            actual_list = actual.to_dict(orient="records")  # type: ignore
        else:
            actual_list = list(actual)
        assert expected == actual_list, f'Test case "{case_name}" failed'
