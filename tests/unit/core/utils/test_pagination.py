"""Unit tests for core utils pagination module."""
from time import time

import pytest

from kili.core.constants import THROTTLING_DELAY
from kili.core.utils.pagination import (
    BatchIteratorBuilder,
    api_throttle,
    batch_object_builder,
)


@pytest.mark.parametrize(
    "name,test_case",
    [
        (
            "When the size of the iterable is not a multiple of the batch_size, I see a success",
            {
                "batch_size": 3,
                "iterable": list(range(7)),
                "expected_result": (i for i in [[0, 1, 2], [3, 4, 5], [6]]),
            },
        )
    ],
)
def test_batch_iterator_builder(name, test_case):
    """Test batch iterator builder."""
    _ = name
    actual = BatchIteratorBuilder(test_case["iterable"], batch_size=test_case["batch_size"])
    expected = test_case["expected_result"]
    assert all(a == b for a, b in zip(actual, expected))


@pytest.mark.parametrize(
    "name,test_case",
    [
        (
            "When I have one property I see that it returns paginated batches",
            {
                "batch_size": 3,
                "properties_to_batch": {"a1": list(range(10))},
                "expected_result": (
                    i
                    for i in [
                        {"a1": [0, 1, 2]},
                        {"a1": [3, 4, 5]},
                        {"a1": [6, 7, 8]},
                        {"a1": [9]},
                    ]
                ),
            },
        ),
        (
            "When I have several iterables I see it creates a common batch",
            {
                "batch_size": 4,
                "properties_to_batch": {
                    "a1": list(range(10)),
                    "a2": list(range(10, 20)),
                    "a3": list(range(20, 30)),
                },
                "expected_result": (
                    i
                    for i in [
                        {
                            "a1": [0, 1, 2, 3],
                            "a2": [10, 11, 12, 13],
                            "a3": [20, 21, 22, 23],
                        },
                        {
                            "a1": [4, 5, 6, 7],
                            "a2": [14, 15, 16, 17],
                            "a3": [24, 25, 26, 27],
                        },
                        {"a1": [8, 9], "a2": [18, 19], "a3": [28, 29]},
                    ]
                ),
            },
        ),
        (
            "When I have None arrays, I see that it stays None in the batches",
            {
                "batch_size": 4,
                "properties_to_batch": {
                    "a1": list(range(10)),
                    "a2": None,
                    "a3": list(range(10, 20)),
                    "a4": None,
                },
                "expected_result": (
                    i
                    for i in [
                        {
                            "a1": [0, 1, 2, 3],
                            "a2": None,
                            "a3": [10, 11, 12, 13],
                            "a4": None,
                        },
                        {
                            "a1": [4, 5, 6, 7],
                            "a2": None,
                            "a3": [14, 15, 16, 17],
                            "a4": None,
                        },
                        {"a1": [8, 9], "a2": None, "a3": [18, 19], "a4": None},
                    ]
                ),
            },
        ),
        (
            "When I have only None, I see it return one batch of None",
            {
                "batch_size": 2,
                "properties_to_batch": {"a1": None, "a2": None, "a3": None},
                "expected_result": (i for i in [{"a1": None, "a2": None, "a3": None}]),
            },
        ),
    ],
)
def test_batch_object_builder(name, test_case):
    """Test batch iterator builder for several arrays in the same time."""
    _ = name
    actual = batch_object_builder(test_case["properties_to_batch"], test_case["batch_size"])
    expected = test_case["expected_result"]
    assert all(a == b for a, b in zip(actual, expected))


def test_when_i_call_api_throttle_given_a_fast_function_then_it_makes_it_last_longer():
    fast_throttled_function = api_throttle(lambda x: x)
    tic = time()
    res = fast_throttled_function(1)
    assert (time() - tic) > THROTTLING_DELAY
    assert res == 1
