"""Kili API Gateway module for interacting with Kili."""

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.asset import AssetOperationMixin
from kili.adapters.kili_api_gateway.issue import IssueOperationMixin
from kili.adapters.kili_api_gateway.project import ProjectOperationMixin
from kili.adapters.kili_api_gateway.tag import TagOperationMixin
from kili.core.graphql.graphql_client import GraphQLClient


class KiliAPIGateway(
    IssueOperationMixin,
    AssetOperationMixin,
    ProjectOperationMixin,
    TagOperationMixin,
):
    """GraphQL gateway to communicate with Kili backend."""

    def __init__(self, graphql_client: GraphQLClient, http_client: HttpClient) -> None:
        """Initialize the Kili API Gateway."""
        self.graphql_client = graphql_client
        self.http_client = http_client
