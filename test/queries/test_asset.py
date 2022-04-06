"""
    Tests assets query.
"""
import os
from kili.client import Kili
from test.utils import burstthrottle

api_key = os.getenv("KILI_USER_API_KEY")
api_endpoint = os.getenv("KILI_API_ENDPOINT")
kili = Kili(api_key=api_key, api_endpoint=api_endpoint)

TEST_CASES = [
    {
        "case": "AAU, When I query assets with first=50, I get the first 50 assets",
        "args": {"first": 50, "disable_tqdm": True},
        "expected_result": [{"id": i} for i in range(50)],
        "expected_type": "list",
    },
    {
        "case": "AAU, When I query assets with first=200, I get the first 200 assets",
        "args": {"first": 200, "disable_tqdm": True},
        "expected_result": [{"id": i} for i in range(200)],
        "expected_type": "list",
    },
    {
        "case": "AAU, When I query assets with first=50 and skip=20, I skip the 20"
        " first assets I get the 50 assets following",
        "args": {"first": 50, "skip": 20, "disable_tqdm": True},
        "expected_result": [{"id": i} for i in range(20, 70)],
        "expected_type": "list",
    },
    {
        "case": "AAU, When I query assets with first=50 and skip=20, I skip the 20"
        "first assets I get the 200 following assets",
        "args": {"first": 200, "skip": 20, "disable_tqdm": True},
        "expected_result": [{"id": i} for i in range(20, 220)],
        "expected_type": "list",
    },
    {
        "case": "AAU, When I query all assets with as_generator=True, I get a generator"
        " that yields all 26000 assets",
        "args": {"as_generator": True},
        "expected_result": [{"id": i} for i in range(26000)],
        "expected_type": "generator",
    },
    {
        "case": "AAU, When I query assets with first=3, as_generator=True I get a generator"
        " that yield the 3 assets",
        "args": {"as_generator": True, "first": 3},
        "expected_result": [{"id": i} for i in range(3)],
        "expected_type": "generator",
    },
    {
        "case": "AAU, When I query assets with first=3, skip=20 as_generator=True I get a "
        "generator that skips the 20 first assets and yield the 3 assets following",
        "args": {"as_generator": True, "first": 3, "skip": 20},
        "expected_result": [{"id": i} for i in range(20, 23)],
        "expected_type": "generator",
    },
    {
        "case": 'AAU, When I query assets with first=50 with format="pandas", I get the '
        "first 50 assets as a pandas DataFrame",
        "args": {"format": "pandas", "first": 50, "disable_tqdm": True},
        "expected_result": [{"id": i} for i in range(50)],
        "expected_type": "DataFrame",
    },
    {
        "case": "AAU, When I query assets with first=26000, I get the first 26000 assets",
        "args": {"first": 26000, "disable_tqdm": True},
        "expected_result": [{"id": i} for i in range(26000)],
        "expected_type": "list",
    },
]


def test_assets(mocker):
    """
    Tests several queries
    """
    count_sample_max = 26000

    @burstthrottle(max_hits=250, minutes=1)
    def mocked_query_assets(skip, count_sample, *_):
        """
        Replaces query assets by a list of assets
        """
        max_range = min(count_sample_max, skip + count_sample)
        res = [{"id": i} for i in range(skip, max_range)]
        return res

    mocker.patch("kili.queries.asset.QueriesAsset._query_assets",
                 side_effect=mocked_query_assets)
    mocker.patch("kili.queries.asset.QueriesAsset.count_assets",
                 return_value=count_sample_max)
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
