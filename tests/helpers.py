"""Common utils functions for tests."""
import os
import traceback
import uuid
from typing import Dict

import requests

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
    """Simulates a query result by returning a list of ids."""
    skip = payload["skip"]
    first = payload["first"]
    max_range = min(COUNT_SAMPLE_MAX, skip + first)
    res = {"data": [{"id": i} for i in range(skip, max_range)]}
    return res


def mocked_count_method(*_):
    """Simulates a count query."""
    return COUNT_SAMPLE_MAX


def debug_subprocess_pytest(result):
    try:
        print(result.output)
    except UnicodeEncodeError:
        print(result.output.encode("utf-8"))
    if result.exception is not None:
        traceback.print_tb(result.exception.__traceback__)
        print(result.exception)
    assert result.exit_code == 0


class LocalDownloader:
    def __init__(self, directory, http_client: requests.Session):
        self.directory = directory
        self.http_client = http_client

    def __call__(self, url):
        content = self.http_client.get(url)
        name = os.path.basename(url)
        path = os.path.join(self.directory, f"{str(uuid.uuid4())}-{name}")
        with open(path, "wb") as file:
            file.write(content.content)
        return path
