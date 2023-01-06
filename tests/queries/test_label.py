"""
    Tests labels query.
"""
from unittest.mock import MagicMock

from kili.queries.label import QueriesLabel
from tests.utils import mocked_count_method, mocked_query_method

mocked_auth = MagicMock()
mocked_auth.client.endpoint = "https://staging.cloud.kili-technology.com/api/label/v2/graphql-fake"

TEST_CASES = [
    {
        "case": "AAU, When I query labels with first=50, I get the first 50 labels",
        "args": {"project_id": "abcdefgh", "first": 50, "disable_tqdm": True},
        "expected_result": [{"id": i} for i in range(50)],
        "expected_type": "list",
    },
    {
        "case": (
            "AAU, When I query labels with first=3, skip=20 as_generator=True I get a "
            "generator that skips the 20 first labels and yield the 3 labels following"
        ),
        "args": {
            "project_id": "abcdefgh",
            "as_generator": True,
            "first": 3,
            "skip": 20,
        },
        "expected_result": [{"id": i} for i in range(20, 23)],
        "expected_type": "generator",
    },
]


def test_labels(mocker):
    """
    Test return type of que assets method
    """
    mocker.patch("kili.queries.label.QueriesLabel._query_labels", side_effect=mocked_query_method)
    mocker.patch("kili.queries.label.QueriesLabel.count_labels", return_value=mocked_count_method)
    for test_case in TEST_CASES:
        case_name = test_case["case"]
        expected = test_case["expected_result"]
        actual = QueriesLabel(mocked_auth).labels(**test_case["args"])
        assert (
            type(actual).__name__ == test_case["expected_type"]
        ), f'Test case "{case_name}" failed'
        assert expected == list(actual), f'Test case "{case_name}" failed'
