"""Kili API Gateway module for interacting with Kili."""
import requests

from kili.adapters.kili_api_gateway.asset import AssetOperationMixin
from kili.adapters.kili_api_gateway.issue import IssueOperationMixin
from kili.adapters.kili_api_gateway.project import ProjectOperationMixin
from kili.core.graphql.graphql_client import GraphQLClient


class KiliAPIGateway(IssueOperationMixin, AssetOperationMixin, ProjectOperationMixin):
    """GraphQL gateway to communicate with Kili backend."""

    def __init__(self, graphql_client: GraphQLClient, http_client: requests.Session):
        self.graphql_client = graphql_client
        self.http_client = http_client
