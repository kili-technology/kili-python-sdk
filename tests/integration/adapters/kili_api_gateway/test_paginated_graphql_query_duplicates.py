from typing import cast
from unittest.mock import MagicMock, call

import pytest

from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
)
from kili.core.constants import QUERY_BATCH_SIZE
from kili.core.graphql.graphql_client import GraphQLClient

QUERY = "query"
COUNT_QUERY = "count_query"
PROJECT_ID = "project_id"
WHERE = {"projectID": PROJECT_ID}
NUMBER_OBJECTS_IN_DB = 250
NUMBER_DUPLICATED_OBJECTS = 40


@pytest.fixture()
def graphql_client() -> GraphQLClient:
    mocked_graphql_client = MagicMock(spec=GraphQLClient)

    def mocked_client_execute(query, payload):
        if query == COUNT_QUERY:
            return {"data": NUMBER_OBJECTS_IN_DB}
        first = cast(int, payload["first"] or QUERY_BATCH_SIZE)
        skip = cast(int, payload["skip"])
        nb_objects_to_return = min(first, NUMBER_OBJECTS_IN_DB + NUMBER_DUPLICATED_OBJECTS - skip)
        assert nb_objects_to_return <= QUERY_BATCH_SIZE
        return {
            "data": [
                {"id": f"id-{i % 200 if i < 220 else (i - 20) % NUMBER_OBJECTS_IN_DB}"}
                for i in range(skip, skip + nb_objects_to_return)
            ]
        }

    mocked_graphql_client.execute.side_effect = mocked_client_execute
    return mocked_graphql_client


def test_should_dedupe_elements_when_unicity_check_is_enabled(
    graphql_client: GraphQLClient,
):
    # Given
    options = QueryOptions(disable_tqdm=False, skip=0, first=None)

    # When
    gen = PaginatedGraphQLQuery(graphql_client).execute_query_from_paginated_call(
        QUERY, WHERE, options, "", COUNT_QUERY, "id"
    )

    # Then
    assert list(gen) == [{"id": f"id-{i}"} for i in range(NUMBER_OBJECTS_IN_DB)]


def test_should_provide_the_right_number_elements_when_unicity_check_is_enabled_and_first_property_set(
    graphql_client: GraphQLClient,
):
    # Given
    options = QueryOptions(disable_tqdm=False, skip=0, first=220)

    # When
    gen = PaginatedGraphQLQuery(graphql_client).execute_query_from_paginated_call(
        QUERY, WHERE, options, "", COUNT_QUERY, "id"
    )

    # Then
    assert list(gen) == [{"id": f"id-{i}"} for i in range(220)]


def test_should_use_count_query_when_unicity_check_is_disabled(
    graphql_client: GraphQLClient,
):
    # Given
    options = QueryOptions(disable_tqdm=False, skip=0, first=None)

    # When
    gen = PaginatedGraphQLQuery(graphql_client).execute_query_from_paginated_call(
        QUERY, WHERE, options, "", COUNT_QUERY
    )

    # Then
    assert len(list(gen)) == NUMBER_OBJECTS_IN_DB
    graphql_client.execute.assert_has_calls(
        [
            call(COUNT_QUERY, {"where": {"projectID": PROJECT_ID}}),
            call(
                QUERY,
                {"where": {"projectID": PROJECT_ID}, "skip": 0, "first": 100},
            ),
            call(
                QUERY,
                {"where": {"projectID": PROJECT_ID}, "skip": 100, "first": 100},
            ),
            call(
                QUERY,
                {
                    "where": {"projectID": PROJECT_ID},
                    "skip": 200,
                    "first": NUMBER_OBJECTS_IN_DB - 200,
                },
            ),
        ]
    )


def test_should_not_use_count_query_when_unicity_check_is_enabled(
    graphql_client: GraphQLClient,
):
    # Given
    options = QueryOptions(disable_tqdm=False, skip=0, first=None)

    # When
    gen = PaginatedGraphQLQuery(graphql_client).execute_query_from_paginated_call(
        QUERY, WHERE, options, "", COUNT_QUERY, "id"
    )

    # Then
    assert len(list(gen)) == NUMBER_OBJECTS_IN_DB
    graphql_client.execute.assert_has_calls(
        [
            call(COUNT_QUERY, {"where": {"projectID": PROJECT_ID}}),
            call(
                QUERY,
                {"where": {"projectID": PROJECT_ID}, "skip": 0, "first": 100},
            ),
            call(
                QUERY,
                {"where": {"projectID": PROJECT_ID}, "skip": 100, "first": 100},
            ),
            call(
                QUERY,
                {"where": {"projectID": PROJECT_ID}, "skip": 200, "first": 100},
            ),
        ]
    )
