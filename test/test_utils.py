from kili.utils import row_generator_from_paginated_calls
from test.utils import mocked_count_method, mocked_query_method

TEST_CASES = [
    {
        "case": "AAU, When I query objects with first=50, I get the first 50 objects",
        "args": {"first": 50},
        "expected_result": ({"id": i} for i in range(50)),
    },
    {
        "case": "AAU, When I query objects with first=200, I get the first 200 objects",
        "args": {"first": 200},
        "expected_result": ({"id": i} for i in range(200)),
    },
    {
        "case": "AAU, When I query objects with first=50 and skip=20, I skip the 20"
        " first objects I get the 50 objects following",
        "args": {"first": 50, "skip": 20},
        "expected_result": ({"id": i} for i in range(20, 70)),
    },
    {
        "case": "AAU, When I query objects with first=50 and skip=20, I skip the 20"
        "first objects I get the 200 following objects",
        "args": {"first": 200, "skip": 20},
        "expected_result": ({"id": i} for i in range(20, 220)),
    },
    {
        "case": "AAU, When I query objects with first=25100, I get the first 25100 objects",
        "args": {"first": 25100},
        "expected_result": ({"id": i} for i in range(25100)),
    },
    {
        "case": "AAU, When I query objects with first=20 and disable_tqdm, I get the first 2O objects",
        "args": {"first": 20, "disable_tqdm": True},
        "expected_result": ({"id": i} for i in range(20)),
    },
    {
        "case": "AAU, When I query objects with first=20, skip=20 and disable_tqdm, I  skip the 20"
        "first objects and I get the 20 following objects",
        "args": {"first": 20, "skip": 20, "disable_tqdm": True},
        "expected_result": ({"id": i} for i in range(20, 40)),
    },
    {
        "case": "AAU, When I query objects with first=0, I get no objects",
        "args": {"first": 0},
        "expected_result": iter(()),
    },
]


def test_row_generator_from_paginated_calls():
    """
        Simulates a count query result by returning a list of ids
    """
    for test_case in TEST_CASES:
        case_name = test_case["case"]
        expected = test_case["expected_result"]
        skip = test_case["args"].get('skip', 0)
        first = test_case["args"].get('first')
        disable_tqdm = test_case["args"].get('disable_tqdm', False)

        actual = row_generator_from_paginated_calls(
            skip,
            first,
            mocked_count_method,
            {},
            mocked_query_method,
            {first, skip},
            [],
            disable_tqdm)
        assert all(a == b for a, b in zip(actual, expected)), \
            f"Test case \"{case_name}\" failed"
        assert type(actual).__name__ == "generator", \
            f"Test case \"{case_name}\" failed"
