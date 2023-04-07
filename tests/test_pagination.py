"""Tests for utils module."""

from typing import Dict
from unittest.mock import MagicMock

import pytest

from kili.core.graphql import QueryOptions
from kili.utils.pagination import BatchIteratorBuilder, batch_object_builder

from .utils import (
    MyGraphQLQuery,
    MyGraphQLWhere,
    ThrottlingError,
    mocked_query_method,
    throttling_mocked_query_method,
)


@pytest.mark.parametrize(
    "name,test_case",
    [
        (
            "When I query objects with first=50, I get the first 50 objects",
            {
                "args": {"first": 50},
                "expected_result": ({"id": i} for i in range(50)),
            },
        ),
        (
            "When I query objects with first=200, I get the first 200 objects",
            {
                "case": "AAU, When I query objects with first=200, I get the first 200 objects",
                "args": {"first": 200},
                "expected_result": ({"id": i} for i in range(200)),
            },
        ),
        (
            (
                "When I query objects with first=50 and skip=20, I skip the 20"
                " first objects I get the 50 objects following"
            ),
            {
                "args": {"first": 50, "skip": 20},
                "expected_result": ({"id": i} for i in range(20, 70)),
            },
        ),
        (
            (
                "When I query objects with first=200 and skip=20, I skip the 20"
                "first objects I get the 200 following objects"
            ),
            {
                "args": {"first": 200, "skip": 20},
                "expected_result": ({"id": i} for i in range(20, 220)),
            },
        ),
        (
            "When I query objects with first=20 and disable_tqdm, I get the first 2O objects",
            {
                "args": {"first": 20, "disable_tqdm": True},
                "expected_result": ({"id": i} for i in range(20)),
            },
        ),
        (
            (
                "When I query objects with first=20, skip=20 and disable_tqdm, I skip the 20"
                "first objects and I get the 20 following objects"
            ),
            {
                "args": {"first": 20, "skip": 20, "disable_tqdm": True},
                "expected_result": ({"id": i} for i in range(20, 40)),
            },
        ),
        (
            "When I query objects with first=0, I get no objects",
            {
                "args": {"first": 0},
                "expected_result": iter(()),
            },
        ),
        (
            "When I query objects with first=1, I get the 1st object",
            {
                "args": {"first": 1},
                "expected_result": ({"id": i} for i in range(1)),
            },
        ),
    ],
)
def test_row_generator_from_paginated_calls(mocker, name, test_case):
    """Simulates a count query result by returning a list of ids."""
    _ = name

    # original
    expected = test_case["expected_result"]
    skip = test_case["args"].get("skip", 0)
    first = test_case["args"].get("first")
    disable_tqdm = test_case["args"].get("disable_tqdm", False)

    options = QueryOptions(first=first, skip=skip, disable_tqdm=disable_tqdm)
    where = MyGraphQLWhere()
    actual = MyGraphQLQuery(
        client=MagicMock(execute=mocked_query_method)
    ).execute_query_from_paginated_call(
        query="", where=where, options=options, post_call_function=None
    )

    assert all(a == b for a, b in zip(actual, expected))
    assert type(actual).__name__ == "generator"


@pytest.mark.parametrize(
    "name,test_case",
    [
        (
            (
                "When I do more queries per minutes than the throttling allows it, the paginator"
                " handles it and makes sure that throttling threshold is not reached."
            ),
            {
                "args": {"first": 1000},
                "expected_result": ({"id": i} for i in range(1000)),
            },
        ),
    ],
)
def test_row_generator_from_paginated_calls_handles_throttled_queries(name, test_case, mocker):
    """ """
    _ = name
    expected = test_case["expected_result"]
    skip = test_case["args"].get("skip", 0)
    first = test_case["args"].get("first")
    disable_tqdm = test_case["args"].get("disable_tqdm", False)

    # the following checks that the mocked query error throws a Throttling error when requested
    # too frequently
    with pytest.raises(ThrottlingError):
        for _ in range(20):
            throttling_mocked_query_method("", {"skip": 0, "first": 10})

    options = QueryOptions(first=first, skip=skip, disable_tqdm=disable_tqdm)
    where = MyGraphQLWhere()
    client_mock = MagicMock(execute=throttling_mocked_query_method)
    actual = MyGraphQLQuery(client=client_mock).execute_query_from_paginated_call(
        query="", where=where, options=options, post_call_function=None
    )

    assert all(a == b for a, b in zip(actual, expected))
    assert type(actual).__name__ == "generator"


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
