"""Common utils functions for tests."""
import os
import traceback
import uuid
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict

import requests

from kili.core.graphql import BaseQueryWhere, GraphQLQuery

COUNT_SAMPLE_MAX = 26000
BURST_THROTTLE_MAX_HITS = 250
BURST_THROTTLE_MINUTES = 1


class MyGraphQLQuery(GraphQLQuery):
    @staticmethod
    def query(fragment: str) -> str:
        return f"not_implemented_query with fragment {fragment}"


class MyGraphQLWhere(BaseQueryWhere):
    def graphql_where_builder(self) -> Dict:
        return {"where": "not_implemented_where"}


class ThrottlingError(Exception):
    """Raised when the function is called too much.

    Used for testing purposes.
    """


class burstthrottle:
    """Decorator that prevents a function from being called more that a certain amount of time
    To create a function that cannot be called more than 250 times in a minute:

    @burstthrottle(max_hits = 250, minutes = 1)
    def my_fun():
        pass
    """

    def __init__(self, max_hits, seconds=0, minutes=1.0, hours=0, error_message="TooManyCalls"):
        self.burst_window = timedelta(seconds=seconds, minutes=minutes, hours=hours)
        self.error_message = error_message
        self.hits = 0
        self.max_hits = max_hits
        self.timestamp = datetime.min

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            now = datetime.now()
            if now < self.timestamp + self.burst_window:
                if self.hits < self.max_hits:
                    self.hits += 1
                    return fn(*args, **kwargs)
                else:
                    self.timestamp = datetime.min
                    self.hits = 0
                    raise ThrottlingError()

            else:
                self.timestamp = datetime.now()
                self.hits = 1
                return fn(*args, **kwargs)

        return wrapper


def mocked_query_method(query, payload):
    """Simulates a query result by returning a list of ids."""
    skip = payload["skip"]
    first = payload["first"]
    max_range = min(COUNT_SAMPLE_MAX, skip + first)
    res = {"data": [{"id": i} for i in range(skip, max_range)]}
    return res


@burstthrottle(max_hits=10, minutes=1.0 / 10)
def throttling_mocked_query_method(query, payload):
    """Simulates a query result by returning a list of ids.

    The decorator makes it crash if there
    is more than 10 calls within 6 seconds.
    """
    skip = payload["skip"]
    first = payload["first"]
    max_range = min(1000, skip + first)
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
    def __init__(self, directory):
        self.directory = directory

    def __call__(self, url):
        content = requests.get(url)
        name = os.path.basename(url)
        path = os.path.join(self.directory, f"{str(uuid.uuid4())}-{name}")
        with open(path, "wb") as file:
            file.write(content.content)
        return path
