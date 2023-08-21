"""Common utils functions for tests."""
from typing import Dict

from kili.core.graphql import BaseQueryWhere, GraphQLQuery

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
