"""Integration tests for core utils pagination module."""

from typing import Dict
from unittest.mock import MagicMock

import pytest

from kili.core.graphql.queries import BaseQueryWhere, GraphQLQuery, QueryOptions

COUNT_SAMPLE_MAX = 26000


class MyGraphQLQuery(GraphQLQuery):
    @staticmethod
    def query(fragment: str) -> str:
        return f"not_implemented_query with fragment {fragment}"


class MyGraphQLWhere(BaseQueryWhere):
    def graphql_where_builder(self) -> Dict:
        return {"where": "not_implemented_where"}


def mocked_query_method(query, payload):
    """Simulate a query result by returning a list of ids."""
    skip = payload["skip"]
    first = payload["first"]
    max_range = min(COUNT_SAMPLE_MAX, skip + first)
    return {"data": [{"id": i} for i in range(skip, max_range)]}


@pytest.mark.parametrize(
    ("name", "test_case"),
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
def test_row_generator_from_paginated_calls(name, test_case):
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
        client=MagicMock(execute=mocked_query_method), http_client=MagicMock()
    ).execute_query_from_paginated_call(
        query="", where=where, options=options, post_call_function=None
    )

    assert all(a == b for a, b in zip(actual, expected))
    assert type(actual).__name__ == "generator"
