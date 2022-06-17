"""
    Tests assets query.
"""
import os
from kili.client import Kili
from test.utils import mocked_count_method, mocked_query_method

api_key = os.getenv("KILI_API_KEY")
api_endpoint = os.getenv("KILI_API_ENDPOINT")
kili = Kili(api_key=api_key, api_endpoint=api_endpoint)

TEST_CASES = [
    {
        "case": "AAU, When I query assets with first=50 and skip=20, I skip the 20"
        " first assets I get the 50 assets following",
        "args": {"project_id": "abcdef", "first": 50, "skip": 20, "disable_tqdm": True},
        "expected_result": [{"id": i} for i in range(20, 70)],
        "expected_type": "list",
    },
    {
        "case": "AAU, When I query assets with first=3, skip=20 as_generator=True I get a "
        "generator that skips the 20 first assets and yield the 3 assets following",
        "args": {"project_id": "abcdef", "as_generator": True, "first": 3, "skip": 20},
        "expected_result": [{"id": i} for i in range(20, 23)],
        "expected_type": "generator",
    },
    {
        "case": 'AAU, When I query assets with first=50 with format="pandas", I get the '
        "first 50 assets as a pandas DataFrame",
        "args": {"project_id": "abcdef", "format": "pandas", "first": 50, "disable_tqdm": True},
        "expected_result": [{"id": i} for i in range(50)],
        "expected_type": "DataFrame",
    },
]


def test_assets(mocker):
    """
    Test return type of que assets method
    """
    mocker.patch("kili.queries.asset.QueriesAsset._query_assets",
                 side_effect=mocked_query_method)
    mocker.patch("kili.queries.asset.QueriesAsset.count_assets",
                 return_value=mocked_count_method)
    for test_case in TEST_CASES:
        case_name = test_case["case"]
        expected = test_case["expected_result"]
        actual = kili.assets(**test_case["args"])
        assert (
            type(actual).__name__ == test_case["expected_type"]
        ), f'Test case "{case_name}" failed'
        if type(actual).__name__ == "DataFrame":
            actual_list = actual.to_dict(orient="records")
        else:
            actual_list = list(actual)
        assert expected == actual_list, f'Test case "{case_name}" failed'
