from kili.utils import row_generator_from_paginated_calls, batch_iterator_builder, batch_iterators_builder
from test.utils import mocked_count_method, mocked_query_method


def test_row_generator_from_paginated_calls():
    """
        Simulates a count query result by returning a list of ids
    """
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


def test_batch_iterator_builder():
    """Test batch iterator builder."""
    TEST_CASE = [{
        'case': 'When the size of the iterable is not a multiple of the batch_size, I see a success',
        'batch_size': 3,
        'iterable': [i for i in range(7)],
        'expected_result': (i for i in [[0, 1, 2], [3, 4, 5], [6]])
    }]
    for test_case in TEST_CASE:
        actual = batch_iterator_builder(
            test_case['iterable'], batch_size=test_case['batch_size'])
        expected = test_case['expected_result']
        case_name = test_case['case']
        assert all(a == b for a, b in zip(actual, expected)
                   ), f"Test case \"{case_name}\" failed"


def test_batch_iterators_builder():
    """Test batch iterator builder for several arrays in the same time."""
    array1 = [i for i in range(10)]
    array2 = [i for i in range(10, 20)]
    array3 = [i for i in range(20, 30)]
    TEST_CASE = [{
        'case': 'When I have one array I see that it return a paginated batches',
        'batch_size': 3,
        'arrays': [array1],
        'expected_result': batch_iterator_builder(array1, batch_size=3)
    },
        {
        'case': 'When I have several iterables I see it creates a common batch',
        'batch_size': 4,
        'arrays': [array1, array2, array3],
        'expected_result': (i for i in [([0, 1, 2, 3], [10, 11, 12, 13], [20, 21, 22, 23]),
                                        ([4, 5, 6, 7], [14, 15, 16, 17],
                                            [24, 25, 26, 27]),
                                        ([8, 9], [18, 19], [28, 29])])
    },
        {
        'case': 'When I have None arrays, I see that it stays None in the batches',
        'batch_size': 4,
        'arrays': [array1, None, array2, None],
        'expected_result': (i for i in [([0, 1, 2, 3], None, [10, 11, 12, 13], None),
                                        ([4, 5, 6, 7], None,  [
                                            14, 15, 16, 17], None),
                                        ([8, 9], None, [18, 19], None)])
    },
        {
            'case': 'When I have only None, I see it return one batch of None',
            'batch_size': 2,
            'arrays': [None, None, None],
            'expected_result': [None, None, None]
    }]
    for test_case in TEST_CASE:
        actual = batch_iterators_builder(
            test_case['arrays'], test_case['batch_size'])
        expected = test_case['expected_result']
        case_name = test_case['case']
        assert all(a == b for a, b in zip(actual, expected)
                   ), f"Test case \"{case_name}\" failed"
