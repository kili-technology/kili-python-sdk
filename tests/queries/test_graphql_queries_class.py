"""Module for testing the graphQLQuery class"""

from typing import Generator
from unittest import TestCase
from unittest.mock import MagicMock, call

from kili.graphql import BaseQueryWhere, GraphQLQuery, QueryOptions
from kili.types import Label

NUMBER_OBJECT_IN_DB = 250


def mocked_client_execute(query, payload):
    if query == "object_query":
        first = payload["first"]
        return {"data": {"data": [{"id": "id"}] * min(first, NUMBER_OBJECT_IN_DB)}}
    return {"data": {"data": NUMBER_OBJECT_IN_DB}}


class FakeQuery(GraphQLQuery):
    FORMAT_TYPE = Label
    FRAGMENT_TYPE = Label

    @staticmethod
    def query(_):
        return "object_query"

    COUNT_QUERY = "count_query"


class FakeWhere(BaseQueryWhere):
    def __init__(self, project_id):
        self.project_id = project_id
        super().__init__()

    def graphql_where_builder(self):
        return {"projectID": self.project_id}


class TestGraphQLQueries(TestCase):
    """General tests of the GrpahQL Query class"""

    def setUp(self):
        """Setup up before every test"""
        self.fake_client = MagicMock()
        self.fake_client.execute = MagicMock(side_effect=mocked_client_execute)
        self.query = FakeQuery(self.fake_client)
        self.where = FakeWhere(project_id="project-id")
        self.fields = ["id"]

    def test_query_all_objects_by_paginated_calls(self):
        options = QueryOptions(disable_tqdm=False)
        self.query(self.where, self.fields, options)
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
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": 200, "first": 100},
                ),
            ]
        )

    def test_query_first_objects(self):
        FIRST = 3
        options = QueryOptions(disable_tqdm=False, first=FIRST)
        self.query(self.where, self.fields, options)
        self.fake_client.execute.assert_has_calls(
            [
                call("count_query", {"where": {"projectID": "project-id"}}),
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": 0, "first": FIRST},
                ),
            ]
        )

    def test_query_skip_objects(self):
        SKIP = 30
        options = QueryOptions(disable_tqdm=False, skip=SKIP)
        self.query(self.where, self.fields, options)
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
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": 200 + SKIP, "first": 100},
                ),
            ]
        )

    def test_query_objects_skip_and_first(self):
        SKIP = 30
        FIRST = 20
        options = QueryOptions(disable_tqdm=False, skip=SKIP, first=FIRST)
        self.query(self.where, self.fields, options)
        self.fake_client.execute.assert_has_calls(
            [
                call("count_query", {"where": {"projectID": "project-id"}}),
                call(
                    "object_query",
                    {"where": {"projectID": "project-id"}, "skip": SKIP, "first": FIRST},
                ),
            ]
        )

    def test_return_type(self):
        options = QueryOptions(disable_tqdm=False)
        result = self.query(self.where, self.fields, options)
        assert isinstance(result, Generator)
