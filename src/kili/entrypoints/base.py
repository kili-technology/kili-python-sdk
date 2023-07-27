"""Base class for entrypoints dealing with GraphQL operations."""
import abc
from typing import Optional, Type, TypeVar

import requests

from kili.core.graphql.graphql_client import GraphQLClient
from kili.core.helpers import format_result

T = TypeVar("T")


class BaseOperationEntrypointMixin(abc.ABC):
    """Base class for entrypoints dealing with GraphQL operations."""

    graphql_client: GraphQLClient
    http_client: requests.Session

    def format_result(self, name: str, result: dict, object_: Optional[Type[T]] = None) -> T:
        """Format the result of a graphQL query.

        FIXME: this should not be used at that level.
        """
        return format_result(name, result, object_, self.http_client)
