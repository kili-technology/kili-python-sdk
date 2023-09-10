"""Module for testing the graphQLQuery class."""

from typing import Generator, cast
from unittest.mock import MagicMock, call

import pytest

from kili.adapters.http_client import HttpClient
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
NUMBER_OBJECT_IN_DB = 250


@pytest.fixture()
def graphql_client() -> GraphQLClient:
    mocked_graphql_client = MagicMock(spec=GraphQLClient)

    def mocked_client_execute(query, payload):
        if query == COUNT_QUERY:
            return {"data": NUMBER_OBJECT_IN_DB}
        first = cast(int, payload["first"] or QUERY_BATCH_SIZE)
        skip = cast(int, payload["skip"])
        nb_objects_to_return = min(first, NUMBER_OBJECT_IN_DB - skip)
        assert nb_objects_to_return <= QUERY_BATCH_SIZE
        return {"data": [{"id": f"id-{i}"} for i in range(skip, skip + nb_objects_to_return)]}

    mocked_graphql_client.execute.side_effect = mocked_client_execute
    return mocked_graphql_client


def test_given_a_query_the_function_returns_a_generator(graphql_client: GraphQLClient):
    # given
    options = QueryOptions(disable_tqdm=False)

    # when
    gen = PaginatedGraphQLQuery(graphql_client).execute_query_from_paginated_call(
        QUERY, WHERE, options, "", COUNT_QUERY
    )

    # then
    assert isinstance(gen, Generator)


def test_given_a_query_it_runs_several_paginated_call_if_needed(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    # given
    options = QueryOptions(disable_tqdm=False)

    # when
    gen = PaginatedGraphQLQuery(graphql_client).execute_query_from_paginated_call(
        QUERY, WHERE, options, "", COUNT_QUERY
    )
    list(gen)

    # then
    print(graphql_client.execute.mock_calls)
    graphql_client.execute.assert_has_calls(
        [
            call(COUNT_QUERY, {"where": {"projectID": PROJECT_ID}}),
            call(QUERY, {"where": {"projectID": PROJECT_ID}, "skip": 0, "first": 100}),
            call(
                QUERY,
                {"where": {"projectID": PROJECT_ID}, "skip": 100, "first": 100},
            ),
            # last call: 50 = NUMBER_OBJECT_IN_DB - QUERY_BATCH_SIZE - QUERY_BATCH_SIZE
            call(
                QUERY,
                {"where": {"projectID": PROJECT_ID}, "skip": 200, "first": 50},
            ),
        ],
    )


def test_given_a_query_with_skip_argument_it_skips_elements(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    # given
    skip = 30
    options = QueryOptions(disable_tqdm=False, skip=skip)

    # when
    gen = PaginatedGraphQLQuery(graphql_client).execute_query_from_paginated_call(
        QUERY, WHERE, options, "", COUNT_QUERY
    )
    list(gen)

    # then
    graphql_client.execute.assert_has_calls(
        [
            call(COUNT_QUERY, {"where": {"projectID": PROJECT_ID}}),
            call(
                QUERY,
                {"where": {"projectID": PROJECT_ID}, "skip": skip, "first": 100},
            ),
            call(
                QUERY,
                {"where": {"projectID": PROJECT_ID}, "skip": 100 + skip, "first": 100},
            ),
            # last call: 20 = NUMBER_OBJECT_IN_DB - skip - QUERY_BATCH_SIZE - QUERY_BATCH_SIZE
            call(
                QUERY,
                {"where": {"projectID": PROJECT_ID}, "skip": 200 + skip, "first": 20},
            ),
        ]
    )


def test_given_a_query_with_skip_and_first_arguments_it_queries_the_right_elements(
    graphql_client: GraphQLClient,
):
    # given
    skip = 30
    first = 20
    options = QueryOptions(disable_tqdm=False, skip=skip, first=first)

    # when
    gen = PaginatedGraphQLQuery(graphql_client).execute_query_from_paginated_call(
        QUERY, WHERE, options, "", COUNT_QUERY
    )
    elements = list(gen)

    # then
    graphql_client.execute.assert_has_calls(
        [
            call(COUNT_QUERY, {"where": {"projectID": PROJECT_ID}}),
            call(
                QUERY,
                {"where": {"projectID": PROJECT_ID}, "skip": skip, "first": first},
            ),
        ]
    )
    assert elements == [{"id": f"id-{i}"} for i in range(skip, skip + first)]


def test_given_a_query_and_a_number_of_elements_to_query_i_have_a_progress_bar(
    graphql_client, capsys
):
    # given
    options = QueryOptions(disable_tqdm=False)

    # when
    gen = PaginatedGraphQLQuery(graphql_client).execute_query_from_paginated_call(
        QUERY, WHERE, options, "", COUNT_QUERY
    )
    list(gen)

    # then
    captured = capsys.readouterr()
    assert "0%|          | 0/250" in captured.err
    assert "100%|██████████| 250/250" in captured.err


def test_given_a_query_without_a_count_query_I_do_not_have_a_progress_bar(graphql_client, capsys):
    # given
    options = QueryOptions(disable_tqdm=False)

    # when
    gen = PaginatedGraphQLQuery(graphql_client).execute_query_from_paginated_call(
        QUERY, WHERE, options, "", None
    )
    list(gen)

    # then
    captured = capsys.readouterr()
    assert captured.err == ""
