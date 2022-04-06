"""
    Tests labels query.
"""
import os
from kili.client import Kili
from test.utils import mocked_count_method, mocked_query_method

api_key = os.getenv("KILI_USER_API_KEY")
api_endpoint = os.getenv("KILI_API_ENDPOINT")
kili = Kili(api_key=api_key, api_endpoint=api_endpoint)

TEST_CASES = [
    {
        "case": "AAU, When I query labels with first=50, I get the first 50 labels",
        "args": {"first": 50, "disable_tqdm": True},
        "expected_result": [{"id": i} for i in range(50)],
        "expected_type": "list",
    },
    {
        "case": "AAU, When I query labels with first=3, skip=20 as_generator=True I get a "
        "generator that skips the 20 first labels and yield the 3 labels following",
        "args": {"as_generator": True, "first": 3, "skip": 20},
        "expected_result": [{"id": i} for i in range(20, 23)],
        "expected_type": "generator",
    },
]


def test_labels(mocker):
    """
        Test return type of que assets method
    """
    mocker.patch("kili.queries.label.QueriesLabel._query_labels",
                 side_effect=mocked_query_method)
    mocker.patch("kili.queries.label.QueriesLabel.count_labels",
                 return_value=mocked_count_method)
    for test_case in TEST_CASES:
        case_name = test_case["case"]
        expected = test_case["expected_result"]
        actual = kili.labels(**test_case["args"])
        assert type(actual).__name__ == test_case["expected_type"], \
            f"Test case \"{case_name}\" failed"
        assert expected == list(actual), f"Test case \"{case_name}\" failed"
