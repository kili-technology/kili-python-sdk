"""Base class for entrypoints dealing with GraphQL operations."""
import abc
from typing import Optional, Type, TypeVar

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.core.graphql.graphql_client import GraphQLClient
from kili.core.helpers import format_result

T = TypeVar("T")


class BaseOperationEntrypointMixin(abc.ABC):
    """Base class for entrypoints dealing with GraphQL operations."""

    # FIXME: graphql_client and http_client should be removed once
    # all methods have been moved to the new architecture
    graphql_client: GraphQLClient
    http_client: HttpClient
    kili_api_gateway: KiliAPIGateway

    def format_result(self, name: str, result: dict, object_: Optional[Type[T]] = None) -> T:
        """Format the result of a graphQL query.

        FIXME: this should not be used at that level.
        """
        return format_result(name, result, object_, self.http_client)
