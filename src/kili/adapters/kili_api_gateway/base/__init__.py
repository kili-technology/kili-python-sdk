"""Base class for all KiliAPIGateway Operation Mixin classes."""

from abc import ABC

from kili.adapters.http_client import HttpClient
from kili.core.graphql.graphql_client import GraphQLClient


class BaseOperationMixin(ABC):
    """Base class for all KiliAPIGateway Operation Mixin classes.

    It is used to share the GraphQL client between all methods classes.

    It is not meant to be used and instantiated directly.
    """

    graphql_client: GraphQLClient  # instantiated in the KiliAPIGateway child class
    http_client: HttpClient  # instantiated in the KiliAPIGateway child class
