"""Module for testing the graphQLQuery class."""

from typing import Generator
from unittest import TestCase
from unittest.mock import MagicMock, call

from kili.constants import QUERY_BATCH_SIZE
from kili.graphql import BaseQueryWhere, GraphQLQuery, QueryOptions

NUMBER_OBJECT_IN_DB = 250


def mocked_client_execute(query, payload):
    if query == "object_query":
        first = payload["first"]
        skip = payload["skip"]
        nb_objects_to_return = min(first, NUMBER_OBJECT_IN_DB - skip)
        assert nb_objects_to_return <= QUERY_BATCH_SIZE, nb_objects_to_return
        return {"data": [{"id": "id"}] * nb_objects_to_return}

    if query == "count_query":
        return {"data": NUMBER_OBJECT_IN_DB}

    raise ValueError(f"Unexpected query: {query}")


class FakeQueryWithCount(GraphQLQuery):
    COUNT_QUERY = "count_query"

    @staticmethod
    def query(_):
        return "object_query"


class FakeQueryWithoutCount(GraphQLQuery):
    @staticmethod
    def query(_):
        return "object_query"


class FakeWhere(BaseQueryWhere):
    def __init__(self, project_id):
        self.project_id = project_id
        super().__init__()

    def graphql_where_builder(self):
        return {"projectID": self.project_id}


class TestGraphQLQueries(TestCase):
    """General tests of the GrpahQL Query class."""

    def setUp(self):
        """Setup up before every test."""
        self.fake_client = MagicMock()
        self.fake_client.execute = MagicMock(side_effect=mocked_client_execute)
        self.where = FakeWhere(project_id="project-id")
        self.fields = ["id"]

    def test_query_all_objects_by_paginated_calls_with_count(self):
        options = QueryOptions(disable_tqdm=False)
        list(FakeQueryWithCount(self.fake_client)(self.where, self.fields, options))
        self.fake_client.execute.assert_has_calls(
            [
                call("count_query", {"where": {"projectID": "project-id"}}),
                call(
                    "object_query", {"where": {"projectID": "project-id"}, "skip": 0, "first": 100}
                ),
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": 100, "first": 100},
                ),
                # last call: 50 = NUMBER_OBJECT_IN_DB - QUERY_BATCH_SIZE - QUERY_BATCH_SIZE
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": 200, "first": 50},
                ),
            ]
        )

    def test_query_all_objects_by_paginated_calls_without_count(self):
        options = QueryOptions(disable_tqdm=False)
        list(FakeQueryWithoutCount(self.fake_client)(self.where, self.fields, options))
        self.fake_client.execute.assert_has_calls(
            [
                call(
                    "object_query", {"where": {"projectID": "project-id"}, "skip": 0, "first": 100}
                ),
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": 100, "first": 100},
                ),
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": 200, "first": 100},
                ),
            ]
        )

    def test_query_first_objects_with_count(self):
        FIRST = 3
        options = QueryOptions(disable_tqdm=False, first=FIRST)
        list(FakeQueryWithCount(self.fake_client)(self.where, self.fields, options))
        self.fake_client.execute.assert_has_calls(
            [
                call("count_query", {"where": {"projectID": "project-id"}}),
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": 0, "first": FIRST},
                ),
            ]
        )

    def test_query_first_objects_without_count(self):
        FIRST = 3
        options = QueryOptions(disable_tqdm=False, first=FIRST)
        list(FakeQueryWithoutCount(self.fake_client)(self.where, self.fields, options))
        self.fake_client.execute.assert_has_calls(
            [
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": 0, "first": FIRST},
                ),
            ]
        )

    def test_query_skip_objects_with_count(self):
        SKIP = 30
        options = QueryOptions(disable_tqdm=False, skip=SKIP)
        list(FakeQueryWithCount(self.fake_client)(self.where, self.fields, options))
        self.fake_client.execute.assert_has_calls(
            [
                call("count_query", {"where": {"projectID": "project-id"}}),
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": SKIP, "first": 100},
                ),
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": 100 + SKIP, "first": 100},
                ),
                # last call: 20 = NUMBER_OBJECT_IN_DB - SKIP - QUERY_BATCH_SIZE - QUERY_BATCH_SIZE
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": 200 + SKIP, "first": 20},
                ),
            ]
        )

    def test_query_skip_objects_without_count(self):
        SKIP = 30
        options = QueryOptions(disable_tqdm=False, skip=SKIP)
        list(FakeQueryWithoutCount(self.fake_client)(self.where, self.fields, options))
        self.fake_client.execute.assert_has_calls(
            [
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": SKIP, "first": 100},
                ),
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": 100 + SKIP, "first": 100},
                ),
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": 200 + SKIP, "first": 100},
                ),
            ]
        )

    def test_query_objects_skip_and_first_with_count(self):
        SKIP = 30
        FIRST = 20
        options = QueryOptions(disable_tqdm=False, skip=SKIP, first=FIRST)
        list(FakeQueryWithCount(self.fake_client)(self.where, self.fields, options))
        self.fake_client.execute.assert_has_calls(
            [
                call("count_query", {"where": {"projectID": "project-id"}}),
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": SKIP, "first": FIRST},
                ),
            ]
        )

    def test_query_objects_skip_and_first_without_count(self):
        SKIP = 30
        FIRST = 20
        options = QueryOptions(disable_tqdm=False, skip=SKIP, first=FIRST)
        list(FakeQueryWithoutCount(self.fake_client)(self.where, self.fields, options))
        self.fake_client.execute.assert_has_calls(
            [
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": SKIP, "first": FIRST},
                ),
            ]
        )

    def test_return_type(self):
        options = QueryOptions(disable_tqdm=False)

        result = FakeQueryWithCount(self.fake_client)(self.where, self.fields, options)
        assert isinstance(result, Generator)

        result = FakeQueryWithoutCount(self.fake_client)(self.where, self.fields, options)
        assert isinstance(result, Generator)
