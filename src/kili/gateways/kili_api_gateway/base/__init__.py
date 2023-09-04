"""Base class for all KiliAPIGateway Operation Mixin classes."""
from abc import ABC

from kili.core.graphql.graphql_client import GraphQLClient


class BaseOperationMixin(ABC):
    """Base class for all KiliAPIGateway Operation Mixin classes.

    It is used to share the GraphQL client between all methods classes.

    It is not meant to be used and instantiated directly.
    """

    graphql_client: GraphQLClient
