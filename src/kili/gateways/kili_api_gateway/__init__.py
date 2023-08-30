"""Kili API Gateway module for interacting with Kili."""
import requests

from kili.core.graphql.graphql_client import GraphQLClient
from kili.gateways.kili_api_gateway.issue import IssueOperationMixin
from kili.gateways.kili_api_gateway.tag import TagOperationMixin


class KiliAPIGateway(IssueOperationMixin, TagOperationMixin):
    """GraphQL gateway to communicate with Kili backend."""

    def __init__(self, graphql_client: GraphQLClient, http_client: requests.Session) -> None:
        self.graphql_client = graphql_client
        self.http_client = http_client
